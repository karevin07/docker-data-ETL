import os

from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator


def create_load_tasks(settings):
    """Create load tasks within a TaskGroup"""
    ###############################################
    # Parameters
    ###############################################

    spark_extra_path = os.path.join(settings.SRC_FOLDER, settings.SPARK_EXTRA_PATH)

    title_input_path = os.path.join(os.path.join(settings.SRC_FOLDER, settings.TRANSFORMATION_OUTPUT),
                                    settings.TRANSFORMATION_OUTPUT_TITLE_FILE)
    word_input_path = os.path.join(os.path.join(settings.SRC_FOLDER, settings.TRANSFORMATION_OUTPUT),
                                   settings.TRANSFORMATION_OUTPUT_WORD_FILE)

    postgres_db = settings.POSTGRES_DB
    postgres_jdbc = settings.POSTGRES_JDBC_URL
    postgres_user = settings.POSTGRES_USER
    postgres_pwd = settings.POSTGRES_PASSWORD

    word_table_name = settings.WORD_TABLE
    title_table_name = settings.TITLE_TABLE

    ###############################################
    # Task Definition
    ###############################################
    start_create_table_task = DummyOperator(task_id="start_create_table")
    start_load_data_task = DummyOperator(task_id="start_load_data")

    postgres_create_title_table = PostgresOperator(
        task_id="create_title_table",
        database=postgres_db,
        postgres_conn_id="postgres_default",
        sql="""
            CREATE TABLE IF NOT EXISTS title (
            link_id INT NOT NULL,
            title VARCHAR NOT NULL);
          """,

    )

    postgres_create_content_table = PostgresOperator(
        task_id="create_content_table",
        database=postgres_db,
        postgres_conn_id="postgres_default",
        sql="""
            CREATE TABLE IF NOT EXISTS content (
            word VARCHAR NOT NULL,
            index INT NOT NULL,
            count INT NOT NULL);
          """,
    )

    spark_job_word_load_postgres = SparkSubmitOperator(
        task_id="spark-load-content-data",
        application="/home/workspace/app/load.py",
        name="load-data",
        conn_id="spark_default",
        verbose=True,
        application_args=[word_input_path, word_table_name, postgres_jdbc, postgres_user, postgres_pwd],
        jars=spark_extra_path,
        driver_class_path=spark_extra_path,
        executor_memory="1g"
    )

    spark_job_title_load_postgres = SparkSubmitOperator(
        task_id="spark-load-title-data",
        application="/home/workspace/app/load.py",
        name="load-data",
        conn_id="spark_default",
        verbose=True,
        application_args=[title_input_path, title_table_name, postgres_jdbc, postgres_user, postgres_pwd],
        jars=spark_extra_path,
        driver_class_path=spark_extra_path,
        executor_memory="1g"
    )

    create_table_tasks = [
        postgres_create_title_table,
        postgres_create_content_table
    ]

    load_tasks = [
        spark_job_word_load_postgres,
        spark_job_title_load_postgres
    ]

    end = DummyOperator(task_id="end")

    for table_task in create_table_tasks:
        start_create_table_task >> table_task
        table_task >> start_load_data_task

    for load_task in load_tasks:
        start_load_data_task >> load_task
        load_task >> end

    return end  # Return last task for chaining
