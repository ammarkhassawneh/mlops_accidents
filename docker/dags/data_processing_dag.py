from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import sys
import os
from pathlib import Path

# Add the path 
sys.path.append('/opt/airflow/ml_model')
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / 'src'))

# from features.build_features import build_features

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'data_processing',
    default_args=default_args,
    description='A DAG to process accident data',
    schedule_interval=timedelta(days=1),
)

def process_data(**kwargs):
    input_filepath = '/opt/airflow/data/raw'
    output_filepath = '/opt/airflow/data/processed'
    
    input_filepath_users = f"{input_filepath}/usagers-2021.csv"
    input_filepath_caract = f"{input_filepath}/caracteristiques-2021.csv"
    input_filepath_places = f"{input_filepath}/lieux-2021.csv"
    input_filepath_veh = f"{input_filepath}/vehicules-2021.csv"
    
    '''X_train, X_test, y_train, y_test = build_features(
        input_filepath_users,
        input_filepath_caract,
        input_filepath_places,
        input_filepath_veh,
        output_filepath
    )'''
    
    print("Data processing completed. Files saved in:", output_filepath)

process_data_task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    provide_context=True,
    dag=dag,
)

process_data_task
