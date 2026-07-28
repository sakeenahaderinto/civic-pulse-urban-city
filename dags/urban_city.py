from datetime import datetime, timedelta

from airflow import DAG
from airflow.sdk import task

from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.microsoft.azure.operators.data_factory import AzureDataFactoryRunPipelineOperator

from include.upload_raw_data import upload_data
from include.transform import transform

default_args = {
    'owner': 'amdari',
    'depends_on_past': False,
    'start_date': datetime(2026, 7, 28),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'schedule_interval': '@hourly',
    'azure_data_factory_conn_id': 'azure_factory',
    'factory_name': 'urban-cities-data-factory',
    'resource_group_name': 'service_requests'
}

@task()
def extract_data_from_api():
    api_response = upload_data()

    return api_response

@task()
def transform_data():
    cleaned_data = transform()

    return cleaned_data

with DAG(dag_id='urban_city_requests',
         catchup=False,
         default_args=default_args):

    create_db_table = SQLExecuteQueryOperator(
        sql='sql/urban_city.sql',
        task_id='urban_city_table',
        conn_id='postgres_conn'
    )

    data_factory = AzureDataFactoryRunPipelineOperator(
        task_id='run_data_factory',
        pipeline_name='UrbanCityDataFactoryPipeline',
    )

    extract_data_from_api() >> transform_data() >> create_db_table >> data_factory


