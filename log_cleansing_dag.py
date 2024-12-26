from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from airflow.models import Variable as V

# DAG 정의
with DAG(
        dag_id='log_cleansing_dag',
        default_args={
            'owner': 'airflow',
            'retries': 1,
            'retry_delay': timedelta(minutes=5),
        },
        schedule='@daily',
        start_date=datetime(2024, 12, 25),
        catchup=False,
) as dag:
    # 시작 태스크: BashOperator로 시작 신호 출력
    start_task = BashOperator(
        task_id='start_task',  # 작업 ID
        bash_command='echo "DAG 시작: 데이터 처리 작업 시작!"'  # Bash 명령어
    )

    spark_host = V.get('spark_host', 'localhost')
    log_cleansing_command = f"""sudo ssh -i ~/.ssh/spark_key.pem ubuntu@{spark_host} \
                                '
                                bash /home/ubuntu/etl/py/common/environ.sh \ 
                                /home/ubuntu/spark/bin/spark-submit \
                                /home/ubuntu/etl/py/common/LogsCleansing.py --bucket tripcok --folder topics/tripcok --date 2024-12-25
                                '
"""

    log_cleansing_task = BashOperator(
        task_id='log_cleansing_task',
        bash_command=log_cleansing_command,  # 템플릿 문자열로 처리됨
    )

    # 종료 태스크: BashOperator로 종료 신호 출력
    end_task = BashOperator(
        task_id='end_task',  # 작업 ID
        bash_command='echo "DAG 종료: 모든 작업 완료!"'  # Bash 명령어
    )

    # 태스크 순서 정의
    start_task >> log_cleansing_task >> end_task
