from airflow import DAG
from airflow.operators.email import EmailOperator
from datetime import datetime
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
import os

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 10, 20)
    # 'retries': 1
}


with DAG(dag_id='bash_example', default_args=default_args, schedule='* * * * *') as dag:

    start_task = EmptyOperator(task_id="start_task")

    test_task = BashOperator(
        task_id="test_task", 
        bash_command='mkdir -p $(pwd)/output && echo "{{ ts }}: Test task completed" >> $(pwd)/output/test.txt'
    )

    end_task = EmptyOperator(
        task_id="end_task"
    )

    start_task >> test_task >> end_task