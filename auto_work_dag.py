from datetime import timedelta, datetime

from airflow import DAG
from airflow.models import Variable as V
from airflow.operators.python import PythonOperator

from utils.autowork_board_v2 import AutoWorkBoard
from utils.autowork_register_login import AutoWorkByLoginRegister
from utils.autowork_group import AutoWorkByGroup
from utils.autowork_group_join import AutoWorkByGroupJoin
from utils.place.place_auto import run_place_api
with DAG(
        dag_id='auto_work_dag',
        default_args={
            'owner': 'airflow',
            'retries': 1,
            'retry_delay': timedelta(minutes=5),
        },
        start_date=datetime(2024, 12, 24),  # start_date 추가
        schedule_interval="*/5 * * * *",
        catchup=False,  # 과거 실행 방지
        tags=['auto', 'ingest', 'log', 'data', 'work']
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


    def run_auto_work_board_task(**kwargs):
        config = get_config_from_variables()
        api_manager = AutoWorkBoard(**config)
        api_manager.run_scenario()


    auto_work_board_task = PythonOperator(
        task_id="auto_work_board_task",
        python_callable=run_auto_work_board_task,
        provide_context=True,
    )


    def run_auto_work_register_login_task(**kwargs):
        config = get_config_from_variables()
        api_manager = AutoWorkByLoginRegister(**config)
        api_manager.run()


    auto_work_register_login_task = PythonOperator(
        task_id="auto_work_register_login_task",
        python_callable=run_auto_work_register_login_task,
        provide_context=True,
    )


    def run_auto_work_group_task(**kwargs):
        config = get_config_from_variables()
        api_manager = AutoWorkByGroup(**config)
        api_manager.run()


    auto_work_group_task = PythonOperator(
        task_id="auto_work_group_task",
        python_callable=run_auto_work_group_task,
        provide_context=True,
    )


    def run_auto_work_group_join_task(**kwargs):
        config = get_config_from_variables()
        api_manager = AutoWorkByGroupJoin(**config)
        api_manager.run()


    auto_work_group_join_task = PythonOperator(
        task_id="auto_work_group_join_task",
        python_callable=run_auto_work_group_join_task,
        provide_context=True,
    )

    def run_auto_work_pdddlace_task(**kwargs):
        run_place_api()

    auto_work_group_place_task = PythonOperator(
        task_id="auto_workd_group_place_task",
        python_callable=run_auto_work_group_place_task,
        provide_context=True,
    )

    auto_work_register_login_task >> auto_work_group_task >> auto_work_group_join_task >> auto_work_board_task
