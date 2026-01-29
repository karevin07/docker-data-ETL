from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup

from pkg.settings import setting as settings
from pkg.etlflow import Extract
from pkg.etlflow.Transformation import create_transformation_tasks
from pkg.etlflow.Load import create_load_tasks


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2000, 1, 1),
    'email': ['kelvin@ghtinc.com'],
    'email_on_failure': False,
    'retries': 0,
    'run_as_user': 'airflow'
}

with DAG(
    'etl_flow',
    default_args=default_args,
    schedule='0 0 * * *',
    catchup=False,
) as dag:

    extract_task = PythonOperator(
        task_id='extract-data',
        python_callable=Extract.main
    )

    with TaskGroup(group_id='transformation-data') as transformation_group:
        create_transformation_tasks(settings)

    with TaskGroup(group_id='load-data') as load_group:
        create_load_tasks(settings)

    extract_task >> transformation_group >> load_group

