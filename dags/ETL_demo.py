from airflow import DAG
from datetime import datetime
from airflow.operators.python_operator import PythonOperator
from airflow.operators.subdag_operator import SubDagOperator

from pkg.settings import setting as settings
from pkg.etlflow import Extract
from pkg.etlflow.Transformation import get_transformation_get_task
from pkg.etlflow.Load import get_load_task


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2000, 1, 1),
    'email': ['kelvin@ghtinc.com'],
    'email_on_failure': False,
    'retries': 0,
    'run_as_user': 'airflow'
}

dag_id = 'etl_flow'
dag = DAG(
    dag_id,
    default_args=default_args,
    schedule_interval='0 0 * * *',
    catchup=False,
)

extract_dag = PythonOperator(
    dag=dag,
    task_id='extract-data',
    python_callable=Extract.main
)

transformation_dag = SubDagOperator(
    dag=dag,
    task_id='transformation-data',
    subdag=get_transformation_get_task(dag_id, settings),
)


load_dag = SubDagOperator(
    dag=dag,
    task_id='load-data',
    subdag=get_load_task(dag_id, settings),
)
extract_dag >> transformation_dag

transformation_dag >> load_dag

