from airflow import DAG
from datetime import datetime
from airflow.operators.bash_operator import BashOperator

from pkg.settings import setting as settings
import os


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2000, 1, 1),
    'email': ['kelvin@ghtinc.com'],
    'email_on_failure': False,
    'retries': 0,
    'run_as_user': 'airflow'
}

dag_id = 'clean_flow'
dag = DAG(
    dag_id,
    default_args=default_args,
    schedule_interval='0 0 * * *',
    catchup=False,
)

clean_dag = BashOperator(
    dag=dag,
    task_id='clean_data',
    bash_command=f'rm -r -f {os.path.join(settings.SRC_FOLDER, "data")}',
)

clean_dag