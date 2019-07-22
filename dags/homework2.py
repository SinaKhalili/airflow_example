"""
Dag file to get some astronaut data as JSON and transform it to csv
"""
import json
import requests
import csv
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator

request = "http://api.open-notify.org/astros.json"

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2019, 7, 21),
    'depends_on_past': False,
    'email': ['khalili@sfu.ca'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}
dag = DAG(
    'space_dag',
    default_args=default_args,
    description='gets astrodata',
    schedule_interval=timedelta(days=10),
)

task1 = BashOperator(
    task_id="blastoff",
    bash_command="echo '🚀 blastoff'",
    dag=dag,
)

def get_current_astronauts(request):
    """
    Get current astronauts from the space api
    """
    json_data =  requests.get(request).json()

    with open('../data/data.json', 'w') as outfile:
        json.dump(json_data, outfile)

task2 = PythonOperator(
    task_id="GET",
    python_callable=get_current_astronauts,
    op_kwargs={'request': request},
    dag=dag
)

def turn_json_into_csv():
    """
    Turns the above json into a csv file
    """
    with open('../data/data.json') as json_file:
        data = json.load(json_file)

        with open('../data/data.csv','w') as csv_file:
            writer = csv.writer(
                csv_file,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL
            )
            print(data)
            for p in data['people']:
                writer.writerow([p['name'], p['craft']])

task3 = PythonOperator(
    task_id="JSON",
    python_callable=turn_json_into_csv,
    dag=dag)

task1 >> task2 >> task3
