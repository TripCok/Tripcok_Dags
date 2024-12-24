from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import  PythonOperator
from datetime import datetime, timedelta

# DAG 정의
with DAG(
    dag_id='test',
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    # SSH를 통한 Spark Submit 명령어
    pick_necessary_json_command = """
        ssh -i ~/.ssh/airflow_key ubuntu@3.38.162.139 '
        /home/ubuntu/spark/bin/spark-submit /home/ubuntu/spark/py/pick_necessary.py
        '
    """
    json2parquet_command = """
        ssh -i ~/.ssh/airflow_key ubuntu@3.38.162.139 '
        /home/ubuntu/spark/bin/spark-submit /home/ubuntu/spark/py/json2parquet.py
        '
    """
    parquet_command = """
        ssh -i ~/.ssh/airflow_key ubuntu@3.38.162.139 '
        /home/ubuntu/spark/bin/spark-submit /home/ubuntu/spark/py/parquet.py
        '
    """

    # 시작 태스크: BashOperator로 시작 신호 출력
    start_task = BashOperator(
        task_id='start_task',  # 작업 ID
        bash_command='echo "DAG 시작: 데이터 처리 작업 시작!"'  # Bash 명령어
    )

    pickjson_task = BashOperator(
        task_id='pickjson_task',
        bash_command=pick_necessary_json_command,
    )

    json2parquet_task = BashOperator(
        task_id='json2parquet_task',
        bash_command=json2parquet_command,
    )

    parquet_task = BashOperator(
        task_id='parquet_task',
        bash_command=parquet_command,
    )

    # 종료 태스크: BashOperator로 종료 신호 출력
    end_task = BashOperator(
        task_id='end_task',  # 작업 ID
        bash_command='echo "DAG 종료: 모든 작업 완료!"'  # Bash 명령어
    )

    start_task >> json2parquet_task >> parquet_task >> end_task
