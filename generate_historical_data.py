import sqlite3
import random
import json
from datetime import datetime, timedelta

TARGET_DB_PATH = 'data/target_dw/target_system.db'

def generate_data():
    conn = sqlite3.connect(TARGET_DB_PATH)
    cursor = conn.cursor()
    
    # 1. ENRICH ETL LOGS (1200+ rows)
    cursor.execute("SELECT DISTINCT etl_pipeline, 'N/A', table_name FROM table_catalog WHERE etl_pipeline != 'N/A' LIMIT 20")
    pipelines = cursor.fetchall() or [
        ('EMR_TO_DW_PATIENT', 'EMR:Patients', 'Dim_Patient'),
        ('EMR_TO_DW_PROVIDER', 'EMR:Providers', 'Dim_Provider'),
        ('FLATFILE_TO_DW_ENCOUNTER', 'CSV:Lab_Results.csv', 'Fact_Clinical_Encounter'),
        ('API_TO_DW_CLAIMS', 'API:clearinghouse.io/claims', 'Fact_Claims')
    ]
    
    start_date = datetime.now() - timedelta(days=365)
    etl_rows = []
    for i in range(1200):
        log_date = start_date + timedelta(minutes=random.randint(0, 365*24*60))
        pipe = random.choice(pipelines)
        p_name = pipe[0] if pipe[0] else 'BATCH_LOAD'
        src = pipe[1] if pipe[1] else 'SOURCE'
        tgt = pipe[2] if pipe[2] else 'TARGET'
        
        status = 'SUCCESS' if random.random() < 0.95 else 'FAILED'
        read = random.randint(100, 2000)
        ins = random.randint(10,read)
        upd = read - ins - random.randint(0,50)
        upd = max(0, upd)
        
        err = ""
        notes = "Incremental batch loaded."
        if status == 'FAILED':
            err = random.choice([
                "Connection Timeout: Remote host flat-lined.",
                "Data Type Mismatch: Cannot cast PK string.",
                "API Throttling: HTTP 429 Too Many Requests.",
                "Disk Full: Out of buffer space on staging."
            ])
            ins, upd = 0, 0
            notes = "Job aborted by runner."
            
        etl_rows.append((
            f"WF_{p_name}", f"MAP_{p_name}", p_name, src, tgt,
            log_date.strftime('%Y-%m-%d %H:%M:%S'), (log_date + timedelta(minutes=random.randint(5,20))).strftime('%Y-%m-%d %H:%M:%S'),
            read, ins, upd, '{}', status, err, notes, f"AUDIT_{random.randint(1000,5000)}"
        ))
        
    cursor.executemany("""
        INSERT INTO etl_execution_logs 
        (workflow_name, mapping_name, pipeline_name, source_system, target_table, start_time, end_time, 
         records_read, records_inserted, records_updated, transformation_metrics, status, error_message, notes, db_audit_ref)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, etl_rows)
    print(f"Inserted {len(etl_rows)} historical ETL logs.")

    # 2. ENRICH BI USAGE (500+ rows)
    reports = [
        'Hospital Readmission Risk Dashboard',
        'Financial Claims Outcome Report',
        'Provider Performance Scorecard',
        'Regional Outbreak Heatmap'
    ]
    users = [
        ('S.Jennings@healthsystem.org','Hospital Administration','Read-Only (Aggregate)'),
        ('C.Thompson@healthsystem.org','Clinical Staff','Read-Only (PHI Unmasked)'),
        ('M.Smith@healthsystem.org','Billing Department','Read/Write (Financial)')
    ]
    
    bi_rows = []
    for i in range(500):
        rep = random.choice(reports)
        usr = random.choice(users)
        log_date = start_date + timedelta(minutes=random.randint(0, 365*24*60))
        bi_rows.append((
            rep, usr[0], usr[1], usr[2],
            random.randint(1, 50), log_date.strftime('%Y-%m-%d %H:%M:%S'), 
            random.choice(['Daily', 'Weekly', 'On-Demand']), 'Top Performance metrics'
        ))
        
    cursor.executemany("""
        INSERT INTO bi_report_usage 
        (report_name, user_email, user_group, access_level, run_count, last_run_timestamp, refresh_frequency, metrics_kpis)
        VALUES (?,?,?,?,?,?,?,?)
    """, bi_rows)
    print(f"Inserted {len(bi_rows)} historical BI usage rows.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    generate_data()
