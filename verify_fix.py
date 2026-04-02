import re
import os
import sys

# Test Regex
result_win = "End-to-End lineage graph generated. View it at: C:\\Users\\jandh\\Documents\\reports\\visualizations\\Fact_Clinical_Encounters_e2e_lineage.html"
result_lin = "End-to-End lineage graph generated. View it at: /content/data-lineage-agent/reports/visualizations/Fact_Clinical_Encounters_e2e_lineage.html"

regex = r'at:\s*(.*\.html)'

m_win = re.search(regex, result_win)
m_lin = re.search(regex, result_lin)

print(f"Windows Match: {m_win.group(1) if m_win else 'FAIL'}")
print(f"Linux Match: {m_lin.group(1) if m_lin else 'FAIL'}")

# Test Tool with ETL
sys.path.append('src')
from agent.agent_tools_ext import generate_e2e_lineage_graph

# Mocking connection path if needed (using default from tool)
print("\nTesting tool with ETL Pipeline 'FLATFILE_TO_DW_CLINICAL'...")
try:
    res = generate_e2e_lineage_graph.run("FLATFILE_TO_DW_CLINICAL")
    print(f"Tool Result: {res}")
except Exception as e:
    print(f"Tool Error: {e}")
