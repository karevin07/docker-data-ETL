import os

from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator


def create_clean_tasks(settings):
    """Create clean tasks within a TaskGroup"""
    input_data = os.path.join(settings.SRC_FOLDER, settings.TRANSFORMATION_INPUT)
    output_data = os.path.join(settings.SRC_FOLDER, settings.TRANSFORMATION_INPUT)
    postgres_db = settings.POSTGRES_DB

    start_clean_task = DummyOperator(task_id="start_clean")
    start_drop_task = DummyOperator(task_id="start_drop")
    finish_task = DummyOperator(task_id="finish")

    clean_input_data_task = BashOperator(
        task_id='clean_input_data',
        bash_command=(
            f'rm -r -f {input_data}'
        ),
    )

    clean_output_data_task = BashOperator(
        task_id='clean_output_data',
        bash_command=(
            f'rm -r -f {output_data}'
        ),
    )

    clean_data_tasks = [clean_input_data_task, clean_output_data_task]

    postgres_drop_title_table = PostgresOperator(
        task_id="drop_title_table",
        database=postgres_db,
        postgres_conn_id="postgres_default",
        sql="""
            DROP TABLE IF EXISTS title ;
          """,

    )

    postgres_drop_content_table = PostgresOperator(
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

    return finish_task  # Return last task for chaining
