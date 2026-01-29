import os

from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.dummy import DummyOperator


def create_transformation_tasks(settings):
    """Create transformation tasks within a TaskGroup"""

    input_path = os.path.join(settings.SRC_FOLDER, settings.TRANSFORMATION_INPUT)
    input_file = os.path.join(input_path, settings.TRANSFORMATION_INPUT_FILE)
    output_path = os.path.join(settings.SRC_FOLDER, settings.TRANSFORMATION_OUTPUT)

    start = DummyOperator(task_id="start")

    spark_job = SparkSubmitOperator(
        task_id="spark_job",
        application="/home/workspace/app/transformation.py",
        name="data-transformation",
        conn_id="spark_default",
        spark_binary='/usr/local/spark/bin/spark-submit',
        application_args=[input_file, output_path]
    )

    end = DummyOperator(task_id="end")

    start >> spark_job >> end

    return end  # Return last task for chaining
