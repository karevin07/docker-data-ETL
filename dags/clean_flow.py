from airflow import DAG
from datetime import datetime
from airflow.operators.bash_operator import BashOperator
from airflow.operators.subdag_operator import SubDagOperator

from pkg.settings import setting as settings
from pkg.etlflow.Clean import get_clear_all_data_dag
import os


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2000, 1, 1),
    'email': ['airflow@airflow.com'],
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


clear_all_data_subdag = SubDagOperator(
    dag=dag,
    task_id='clear_all_data',
    subdag=get_clear_all_data_dag(dag_id, settings),
)

clear_all_data_subdag