from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

sys.path.append('/opt/airflow')

# Ajoutez les chemins nécessaires
sys.path.append('/opt/airflow')
sys.path.append('/opt/airflow/ml_model')

# Importez vos modules
from ml_model.data.check_structure import main as check_structure_main
from ml_model.data.make_dataset import main as make_dataset_main
from ml_model.build_features import build_features
from ml_model.predict_model import predict_severity


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'accident_prediction',
    default_args=default_args,
    description='Pipeline de prédiction des accidents',
    schedule_interval=timedelta(days=1),
)

# Définissez vos tâches ici
check_structure_task = PythonOperator(
    task_id='check_structure',
    python_callable=check_structure_main,
    dag=dag,
)

make_dataset_task = PythonOperator(
    task_id='make_dataset',
    python_callable=make_dataset_main,
    dag=dag,
)

build_features_task = PythonOperator(
    task_id='build_features',
    python_callable=build_features,
    dag=dag,
)

predict_task = PythonOperator(
    task_id='predict',
    python_callable=predict_severity,
    dag=dag,
)

# Définissez l'ordre des tâches
check_structure_task >> make_dataset_task >> build_features_task >> predict_task
