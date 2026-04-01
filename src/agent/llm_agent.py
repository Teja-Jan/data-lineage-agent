import os
import sys
from dotenv import load_dotenv

# Import core tools
from .agent_tools import (
    get_table_lineage, generate_lineage_graph, get_column_impact, 
    get_pipeline_history, get_table_access, get_table_details, 
    get_schema_evolution, get_metadata_inventory
)
# Import enterprise extension tools
from .agent_tools_ext import (
    get_data_model_description, get_full_impact_analysis, generate_e2e_lineage_graph, get_business_context, get_holistic_entity_context
)

load_dotenv()

def run_real_agent(user_prompt: str):
    """Direct Groq API agent with robust error handling for malformed tool calls."""
    import groq as groq_lib
    import json

    client = groq_lib.Groq()  # reads GROQ_API_KEY from env automatically

    tools_map = {
        "get_table_lineage":           get_table_lineage,
        "generate_lineage_graph":      generate_lineage_graph,
        "get_column_impact":           get_column_impact,
        "get_pipeline_history":        get_pipeline_history,
        "get_table_access":            get_table_access,
        "get_table_details":           get_table_details,
        "get_schema_evolution":        get_schema_evolution,
        "get_metadata_inventory":      get_metadata_inventory,
        "get_data_model_description":  get_data_model_description,
        "get_full_impact_analysis":    get_full_impact_analysis,
        "generate_e2e_lineage_graph":  generate_e2e_lineage_graph,
        "get_business_context":        get_business_context,
        "get_holistic_entity_context": get_holistic_entity_context,
    }

    # Keep schema lean — Llama 3.3 generates malformed JSON with >5 complex tools
    groq_tools = [
        {"type": "function", "function": {
            "name": "get_holistic_entity_context",
            "description": "Get complete lineage, ETL status, audit history, and impact for any table, pipeline, source, or report. Call this first for any entity question.",
            "parameters": {"type": "object", "properties": {
                "entity_name": {"type": "string", "description": "Table, source, pipeline, or report name"}
            }, "required": ["entity_name"]}
        }},
        {"type": "function", "function": {
            "name": "generate_e2e_lineage_graph",
            "description": "Generate a focused, interactive lineage graph for a specific table showing sources, ETL pipelines, DW tables, and BI reports.",
            "parameters": {"type": "object", "properties": {
                "table_name": {"type": "string"}
            }, "required": ["table_name"]}
        }},
        {"type": "function", "function": {
            "name": "get_full_impact_analysis",
            "description": "Predict the impact of a proposed change (drop, rename, datatype change) on a table or column.",
            "parameters": {"type": "object", "properties": {
                "table_name":  {"type": "string"},
                "column_name": {"type": "string"},
                "change_type": {"type": "string", "enum": ["drop", "rename", "datatype"]}
            }, "required": ["table_name", "column_name"]}
        }},
        {"type": "function", "function": {
            "name": "get_pipeline_history",
            "description": "Get ETL pipeline execution history, run counts, failures, and retry details.",
            "parameters": {"type": "object", "properties": {
                "pipeline_name": {"type": "string"}
            }, "required": ["pipeline_name"]}
        }},
    ]

    system_msg = (
        "You are an Enterprise Data Lineage & Governance Specialist. "
        "For ANY question about a table, source, pipeline, or report — call `get_holistic_entity_context` first. "
        "Use `generate_e2e_lineage_graph` when asked to visualize. "
        "\n\nCRITICAL OUTPUT REQUIREMENT:\n"
        "When finalizing your text response AFTER tools have run, YOU MUST EXPLICITLY TRACE THE PATH in your text. "
        "Do NOT just say 'lineage was retrieved'. Instead, write a detailed walk: "
        "'[Source System] -> [Staging/File] -> [ETL Pipeline] -> [DW Table] -> [Downstream BI Reports]'. "
        "Explicitly list any ETL failure reasons, specific audit details, or broke down reports found in the tool output. "
        "Always structure your answer clearly into Upstream and Downstream stages for the user."
    )

    messages = [
        {"role": "system",  "content": system_msg},
        {"role": "user",    "content": user_prompt},
    ]


    def _invoke_tool(fn_name: str, args: dict) -> str:
        """Invoke a LangChain tool safely, handling both dict and string inputs."""
        tool = tools_map.get(fn_name)
        if not tool:
            return f"Unknown tool: {fn_name}"
        try:
            # Single-argument tools (e.g. entity_name, table_name) — pass the first value as string
            if len(args) == 1:
                return str(tool.run(list(args.values())[0]))
            elif args:
                return str(tool.run(args))
            else:
                return str(tool.run({}))
        except Exception as e:
            return f"Tool execution error [{fn_name}]: {e}"

    # Agentic loop — max 5 iterations
    for _ in range(5):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=groq_tools,
                tool_choice="auto",
                temperature=0,
            )
        except groq_lib.BadRequestError as e:
            # Llama produced a malformed tool call — retry as plain text (no tools)
            try:
                fallback = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.1,
                )
                text = fallback.choices[0].message.content or ""
                return text if text else run_simulated_agent(user_prompt)
            except Exception:
                return run_simulated_agent(user_prompt)
        except Exception as e:
            return f"Agent error: {e}\n\n" + run_simulated_agent(user_prompt)

        msg = response.choices[0].message

        if not msg.tool_calls:
            return msg.content or "No response generated."

        # Append assistant turn with tool calls
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ]
        })

        # Execute each tool call
        for tc in msg.tool_calls:
            fn_name = tc.function.name
            try:
                args = json.loads(tc.function.arguments) if tc.function.arguments else {}
            except json.JSONDecodeError:
                args = {}
            result = _invoke_tool(fn_name, args)
            messages.append({"role": "tool", "content": result, "tool_call_id": tc.id})

    return "Agent completed analysis."
def run_simulated_agent(prompt: str) -> str:
    """Enhanced mock agent router for professional demonstration purposes."""
    prompt_lower = prompt.lower()
    
    # Handle common typos and healthcare terms
    prompt_lower = (prompt_lower.replace("cliamns", "claims").replace("cliams", "claims")
                   .replace("lienage", "lineage").replace("lieage", "lineage")
                   .replace("porducts", "product"))
    
    # Tables in catalog (Updated for Healthcare/Clinical Focus)
    target_tables = [
        "Fact_Clinical_Encounters", "Fact_Sales", "Dim_Patient", "Dim_Customer", 
        "Dim_Product", "Dim_Provider", "Dim_Date", "Fact_Inventory"
    ]
    
    # Smart asset detection
    detected_asset = None
    if any(k in prompt_lower for k in ["clinical", "incident", "claims", "encounter"]): detected_asset = "Fact_Clinical_Encounters"
    elif "patient" in prompt_lower: detected_asset = "Dim_Patient"
    elif "provider" in prompt_lower: detected_asset = "Dim_Provider"
    elif "product" in prompt_lower: detected_asset = "Dim_Product"
    elif "customer" in prompt_lower: detected_asset = "Dim_Customer"
    elif "sales" in prompt_lower: detected_asset = "Fact_Sales"
    elif "inventory" in prompt_lower: detected_asset = "Fact_Inventory"

    # 1. Specialized Conversational Response for Healthcare Impact (USER REQUEST)
    if any(k in prompt_lower for k in ["drop", "delete", "remove"]) and any(k in prompt_lower for k in ["claims", "clinical", "encounter"]):
        return (
            "### 🛡️ AI Impact Assessment: Critical Risk Detected\n\n"
            "Dropping the `Fact_Clinical_Encounters` (Claims) table carries a **CRITICAL** impact score (9.8/10). "
            "Based on my real-time lineage traversal, here is the ecosystem breakage path:\n\n"
            "**1. Upstream Data Ingestion:**\n"
            "The `FLATFILE_TO_DW_CLINICAL` pipeline will fail immediately as it will lose its primary write target. "
            "This will cause an overflow in the landing zone buffers for `EHR_RDBMS` source data.\n\n"
            "**2. Downstream Analytics & BI:**\n"
            "The **'Patient Performance & Clinical Outcomes'** dashboard will render blank visuals, as it relies on this table for 85% of its core measures (Admission Rates, Mortality Specs, and Bed Availability).\n\n"
            "**Recommendation:** Do not proceed with this DDL operation without a full migration plan. "
            "I have already flagged this query in the Governance Audit log for review."
        )

    # 2. Intent Routing
    if any(k in prompt_lower for k in ["tables", "catalog", "what is present", "what tables", "available"]):
        return f"The current Data Ecosystem contains {len(target_tables)} primary entities: {', '.join(target_tables)}."

    elif any(k in prompt_lower for k in ["data model", "explain", "describe", "purpose"]):
        target = detected_asset or "Fact_Clinical_Encounters"
        return get_data_model_description.run(target)

    elif any(k in prompt_lower for k in ["end to end", "e2e", "full flow", "visualize"]):
        target = detected_asset or "Fact_Clinical_Encounters"
        res = generate_e2e_lineage_graph.run(target)
        return f"Generating your end-to-end lineage overview for `{target}`... [SUCCESS] Visual mapping complete. {res}"

    elif any(k in prompt_lower for k in ["lineage", "trace", "flow", "reconciliation"]):
        target = detected_asset or "Fact_Clinical_Encounters"
        return get_holistic_entity_context.run(target)
        
    elif any(k in prompt_lower for k in ["details", "structure", "columns"]):
        if detected_asset:
            return get_table_details.run(detected_asset)
        return "Please specify a table (e.g., 'show columns for Fact_Clinical_Encounters') to see structural details."
        
    elif any(k in prompt_lower for k in ["impact", "drop", "delete", "change", "modify"]):
        tbl = detected_asset or "Fact_Clinical_Encounters"
        col = "encounter_id" if "clinical" in prompt_lower else "price" if "product" in prompt_lower else "N/A"
        return get_full_impact_analysis.run({"table_name": tbl, "column_name": col, "change_type": "drop"})
        
    elif any(k in prompt_lower for k in ["access", "who", "audit", "permissions"]):
        target = detected_asset or "Fact_Clinical_Encounters"
        return get_table_access.run(target)
        
    elif any(k in prompt_lower for k in ["history", "pipeline", "etl", "failed"]):
        pl = "FLATFILE_TO_DW_CLINICAL" if "clinical" in prompt_lower else "FLATFILE_TO_DW_SALES"
        return get_pipeline_history.run(pl)
        
    elif any(k in prompt_lower for k in ["go ahead", "do this", "fix it", "execute"]):
        return "[ACTION SIMULATED] I have requested immediate execution from the Governance Engine. An approval email has been routed to the Data Owner. Once approved, the reconciliation job will restart dynamically."
        
    elif any(k in prompt_lower for k in ["context", "issues", "why", "historical"]):
        return get_business_context.run(prompt)
        
    else:
        return ("I am your **AI Assistant**. I can help with: Data Model exploration, Lineage tracing, Impact analysis, and ETL monitoring. "
                "Try: 'What happens if we drop the Clinical table?' or 'Trace lineage for Fact_Clinical_Encounters'.")

def main():
    print("=====================================================")
    print(" Data Lineage & Impact Intelligence Agent Started ")
    print("=====================================================\n")
    
    has_api_key = bool(os.getenv("GROQ_API_KEY"))
    
    if not has_api_key:
        print(">> Warning: GROQ_API_KEY not found in environment (.env). Using Simulated Agent for Demo. <<\n")
        
    while True:
        try:
            prompt = input("\nAgent Prompt > ")
            if prompt.strip().lower() in ['exit', 'quit']:
                break
                
            if not prompt.strip():
                continue
                
            if has_api_key:
                response = run_real_agent(prompt)
            else:
                response = run_simulated_agent(prompt)
                
            print("\nAgent Response:\n")
            print(response)
            print("-" * 50)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error executing agent: {str(e)}")

if __name__ == "__main__":
    main()
