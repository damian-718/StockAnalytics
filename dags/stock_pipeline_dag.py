from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 2, 11),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'stock_analytics_pipeline',
    default_args=default_args,
    description='End-to-end stock data pipeline with AI insights',
    schedule_interval='0 * * * *',  # Run every hour
    catchup=False,
)

# Task 1: Ingest candles from Coinbase
ingest_task = BashOperator(
    task_id='ingest_candles',
    bash_command='cd /opt/airflow && docker-compose run --rm ingest-candles',
    dag=dag,
)

# Task 2: Process candles with Spark
process_task = BashOperator(
    task_id='process_candles',
    bash_command='cd /opt/airflow && docker-compose run --rm process-candles',
    dag=dag,
)

# Task 3: Compute metrics
metrics_task = BashOperator(
    task_id='compute_metrics',
    bash_command='cd /opt/airflow && docker-compose run --rm compute-metrics',
    dag=dag,
)

# Task 4: Generate AI report
report_task = BashOperator(
    task_id='generate_report',
    bash_command='cd /opt/airflow && docker-compose run --rm generate-report',
    dag=dag,
)

# Define task dependencies (DAG structure)
ingest_task >> process_task >> metrics_task >> report_task