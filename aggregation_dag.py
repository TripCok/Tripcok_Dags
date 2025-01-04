from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from airflow.models import Variable as V
from airflow.sensors.external_task import ExternalTaskSensor

# DAG 정의
with DAG(
        dag_id='aggregation_dag',
        default_args={
            'owner': 'airflow',
            'retries': 1,
            'retry_delay': timedelta(minutes=5),
        },
        schedule='2 15 * * *',
        start_date=datetime(2024, 12, 25),
        catchup=False,
) as dag:

    # 이전 Dag 동작 감지 Task
    wait_for_log_cleansing = ExternalTaskSensor(
        task_id='wait_for_log_cleansing_task',
        external_dag_id='log_cleansing_dag',
        external_task_id='end_task',
        allowed_states=['success'],
        execution_date_fn=lambda dt: dt,
        mode='poke',
        timeout=3600,
    )

    # 시작 태스크: BashOperator로 시작 신호 출력
    start_task = BashOperator(
        task_id='start_task',
        bash_command='echo "DAG 시작: 집계 ETL 시작"'
    )

    spark_home = "/home/ubuntu/spark/bin/spark-submit"

    # Aggregation 태스크 동적 생성
    aggregation_tasks = []
    for file in [
        "created_group_counting.py",
        "top_application_groups.py",
        "top_group_categories.py",
    ]:
        task = BashOperator(
            task_id=f'{file.replace(".py", "")}_task',
            bash_command=f"""
                sudo ssh -i ~/.ssh/spark_key.pem ubuntu@{{{{ params.spark_host }}}} '
                    bash /home/ubuntu/etl/py/common/environ.sh && \
                    {spark_home} /home/ubuntu/etl/py/aggregation/{file} \
                    --date {{{{ ds }}}}
                '
                """,
            params={'spark_host': V.get('spark_host', 'localhost')},
        )
        aggregation_tasks.append(task)

    end_task = BashOperator(
        task_id='end_task',
        bash_command='echo "DAG 종료: 집계 ETL 완료"'
    )

    wait_for_log_cleansing >> start_task >> aggregation_tasks >> end_task
