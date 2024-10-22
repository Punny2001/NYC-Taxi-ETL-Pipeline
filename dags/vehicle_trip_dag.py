import sys
import os
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator

default_args ={ 
    'owner': 'Krissanapong',
    'start_date': datetime(2023,1,1)
}

dag = DAG(dag_id="vehicle_trip", default_args=default_args, schedule='0 0 * * *')

start_process = EmptyOperator(
    task_id="start_process",
    dag=dag
)

# run_1st_pipeline = PythonOperator(
#     task_id="process_1st_pipeline",
#     python_callable=pipeline_1st,
#     op_kwargs={'forced_date': '{{ ds }}'},
#     dag=dag
# )

# run_2nd_pipeline = PythonOperator(
#     task_id="process_2nd_pipeline",
#     python_callable=pipeline_2nd,
#     op_kwargs={'forced_date': '{{ ds }}'},
#     dag=dag
# )

end_process = EmptyOperator(
    task_id="end_process"
)

# start_process >> [run_1st_pipeline, run_2nd_pipeline] >> end_process
    