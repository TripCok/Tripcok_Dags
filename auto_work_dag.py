from datetime import timedelta

from airflow import DAG
from airflow.models import Variable as V
from airflow.operators.python import PythonOperator

from utils.autowork_board_v2 import AutoWorkBoard

with DAG(
        dag_id='auto_work_dag',
        default_args={
            'owner': 'airflow',
            'retries': 1,
            'retry_delay': timedelta(minutes=5),
        },
        schedule_interval="*/5 * * * *",
) as dag:
    def get_config_from_variables():
        return {
            "server_host": V.get("server_host", default_var="localhost"),
            "server_port": V.get("server_port", default_var="8000"),
            "db_host": V.get("db_host", default_var="localhost"),
            "db_port": int(V.get("db_port", default_var=3306)),
            "db_user": V.get("db_user", default_var="root"),
            "db_password": V.get("db_password", default_var=""),
            "db_database": V.get("db_database", default_var="test"),
        }


    def run_scenario_with_variables(**kwargs):
        config = get_config_from_variables()
        api_manager = AutoWorkBoard(**config)
        api_manager.run_scenario()


    run_scenario_task = PythonOperator(
        task_id="run_api_scenario",
        python_callable=run_scenario_with_variables,
        provide_context=True,
    )
