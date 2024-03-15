import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.operators.dummy_operator import DummyOperator


def get_transformation_get_task(parent_dag_name, settings):

    input_path = os.path.join(settings.SRC_FOLDER, settings.TRANSFORMATION_INPUT)
    input_file = os.path.join(input_path, settings.TRANSFORMATION_INPUT_FILE)
    output_path = os.path.join(settings.SRC_FOLDER, settings.TRANSFORMATION_OUTPUT)
    spark_extra_path = os.path.join(settings.SRC_FOLDER, settings.SPARK_EXTRA_PATH)
    output_word_path = os.path.join(os.path.join(settings.SRC_FOLDER, settings.TRANSFORMATION_OUTPUT),
                                    settings.TRANSFORMATION_OUTPUT_WORD_FILE)
    output_title_path = os.path.join(os.path.join(settings.SRC_FOLDER, settings.TRANSFORMATION_OUTPUT),
                                    settings.TRANSFORMATION_OUTPUT_TITLE_FILE)

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
        dag_id=f"{parent_dag_name}.transformation-data",
        description="This DAG runs a Pyspark to transformation data.",
        default_args=default_args,
        schedule_interval=timedelta(1)
    )

    start = DummyOperator(task_id="start", dag=dag)

    spark_job = SparkSubmitOperator(
        task_id="spark_job",
        application="/home/workspace/app/transformation.py",
        name="data-transformation",
        conn_id="spark_default",
        spark_binary='/usr/local/spark/bin/spark-submit',
        application_args=[input_file,
                        output_path
                        ],
        dag=dag)

    end = DummyOperator(task_id="end", dag=dag)

    start >> spark_job >> end

    return dag
