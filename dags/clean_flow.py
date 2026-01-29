from airflow import DAG
from datetime import datetime
from airflow.utils.task_group import TaskGroup

from pkg.settings import setting as settings
from pkg.etlflow.Clean import create_clean_tasks


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2000, 1, 1),
    'email': ['airflow@airflow.com'],
    'email_on_failure': False,
    'retries': 0,
    'run_as_user': 'airflow'
}

with DAG(
    'clean_flow',
    default_args=default_args,
    schedule='0 0 * * *',
    catchup=False,
) as dag:

    with TaskGroup(group_id='clear_all_data') as clean_group:
        create_clean_tasks(settings)