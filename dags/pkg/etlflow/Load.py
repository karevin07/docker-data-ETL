import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator

from datetime import datetime, timedelta

from airflow.operators.postgres_operator import PostgresOperator


def get_load_task(parent_dag_name, settings):
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
    # DAG Definition
    ###############################################
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
        dag_id=f"{parent_dag_name}.load-data",
        description="This DAG is a sample of integration between Spark and DB. It reads CSV files, load them into a Postgres DB and then read them from the same Postgres DB.",
        default_args=default_args,
        schedule_interval=timedelta(1)
    )

    start_create_table_task = DummyOperator(task_id="start_create_table", dag=dag)
    start_load_data_task = DummyOperator(task_id="start_load_data", dag=dag)

    postgres_create_title_table = PostgresOperator(
        dag=dag,
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
        dag=dag,
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
        executor_memory="1g",
        dag=dag
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
        executor_memory="1g",
        dag=dag
    )

    create_table_tasks = [
        postgres_create_title_table,
        postgres_create_content_table
    ]

    load_tasks = [
        spark_job_word_load_postgres,
        spark_job_title_load_postgres
    ]

    end = DummyOperator(task_id="end", dag=dag)

    for table_task in create_table_tasks:
        start_create_table_task >> table_task
        table_task >> start_load_data_task

    for load_task in load_tasks:
        start_load_data_task >> load_task
        load_task >> end

    return dag
