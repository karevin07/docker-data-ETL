import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator

from datetime import datetime, timedelta


def get_load_task(parent_dag_name, settings):
    # Create spark session

    ###############################################
    # Parameters
    ###############################################
    spark_master = "spark://spark:7077"

    spark_extra_path = os.path.join(settings.SRC_FOLDER, settings.SPARK_EXTRA_PATH)

    title_input_path = os.path.join(os.path.join(settings.SRC_FOLDER, settings.TRANSFORMATION_OUTPUT),
                                    settings.TRANSFORMATION_OUTPUT_TITLE_FILE)
    word_input_path = os.path.join(os.path.join(settings.SRC_FOLDER, settings.TRANSFORMATION_OUTPUT),
                                   settings.TRANSFORMATION_OUTPUT_WORD_FILE)
    postgres_db = settings.POSTGRES_DB
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

    start = DummyOperator(task_id="start", dag=dag)

    spark_job_word_load_postgres = BashOperator(
        dag=dag,
        task_id='clean_data',
        bash_command='spark-submit'
                     f' --master {spark_master}'
                     f' --name data-load'
                     f' /usr/local/spark/app/load.py'
                     f' {word_input_path}'
                     f' {word_table_name}'
                     f' {postgres_db}'
                     f' {postgres_user}'
                     f' {postgres_pwd}'
        ,
    )

    spark_job_title_load_postgres = BashOperator(
        dag=dag,
        task_id='spark-data-load',
        bash_command='spark-submit'
                     f' --master {spark_master}'
                     f' --name data-load'
                     f' /usr/local/spark/app/load.py'
                     f' {title_input_path}'
                     f' {title_table_name}'
                     f' {postgres_db}'
                     f' {postgres_user}'
                     f' {postgres_pwd}'
        ,
    )

    # spark_job_word_load_postgres = SparkSubmitOperator(
    #     task_id="spark-load-word-data",
    #     application="/usr/local/spark/app/load.py",  # Spark application path created in airflow and spark cluster
    #     name="load-data",
    #     conn_id="spark_default",
    #     verbose=1,
    #     conf={"spark.master": spark_master},
    #     application_args=[word_input_path, word_table_name, postgres_db, postgres_user, postgres_pwd],
    #     jars=spark_extra_path,
    #     driver_class_path=spark_extra_path,
    #     dag=dag
    # )
    #
    # spark_job_title_load_postgres = SparkSubmitOperator(
    #     task_id="spark-load-word-data",
    #     application="/usr/local/spark/app/load.py",  # Spark application path created in airflow and spark cluster
    #     name="load-data",
    #     conn_id="spark_default",
    #     verbose=1,
    #     conf={"spark.master": spark_master},
    #     application_args=[title_input_path, title_table_name, postgres_db, postgres_user, postgres_pwd],
    #     jars=spark_extra_path,
    #     driver_class_path=spark_extra_path,
    #     dag=dag
    # )

    tasks = [
        spark_job_word_load_postgres,
        spark_job_title_load_postgres
    ]

    end = DummyOperator(task_id="end", dag=dag)

    for t in tasks:
        start >> t
        t >> end

    return dag