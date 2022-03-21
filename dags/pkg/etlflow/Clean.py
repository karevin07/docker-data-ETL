import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator


def get_clear_all_data_dag(parent_dag_name, settings):
    input_data = os.path.join(settings.SRC_FOLDER, settings.TRANSFORMATION_INPUT)
    output_data = os.path.join(settings.SRC_FOLDER, settings.TRANSFORMATION_INPUT)
    postgres_db = settings.POSTGRES_DB
    now = datetime.now()

    default_args = {
        "owner": "airflow",
        "depends_on_past": False,
        "start_date": datetime(now.year, now.month, now.day),
        "email": ["airflow@airflow.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=1),
        "run_as_user": "airflow"
    }

    dag = DAG(
        dag_id=f"{parent_dag_name}.clear_all_data",
        description="This DAG runs a Pyspark to transformation data.",
        default_args=default_args,
        schedule_interval=timedelta(1)
    )

    start_clean_task = DummyOperator(task_id="start_clean", dag=dag)
    start_drop_task = DummyOperator(task_id="start_drop", dag=dag)
    finish_task = DummyOperator(task_id="finish", dag=dag)

    clean_input_data_task = BashOperator(
        dag=dag,
        task_id='clean_input_data',
        bash_command=(
            f'rm -r -f {input_data}'
        ),
    )

    clean_output_data_task = BashOperator(
        dag=dag,
        task_id='clean_output_data',
        bash_command=(
            f'rm -r -f {output_data}'
        ),
    )

    clean_data_tasks = [clean_input_data_task, clean_output_data_task]

    postgres_drop_title_table = PostgresOperator(
        dag=dag,
        task_id="drop_title_table",
        database=postgres_db,
        postgres_conn_id="postgres_default",
        sql="""
            DROP TABLE IF EXISTS title ;
          """,

    )

    postgres_drop_content_table = PostgresOperator(
        dag=dag,
        task_id="drop_content_table",
        database=postgres_db,
        postgres_conn_id="postgres_default",
        sql="""
            DROP TABLE IF EXISTS content ;
          """,
    )

    drop_table_tasks = [postgres_drop_title_table, postgres_drop_content_table]

    for clean in clean_data_tasks:
        start_clean_task >> clean
        clean >> start_drop_task

    for drop in drop_table_tasks:
        start_drop_task >> drop
        drop >> finish_task

    return dag
