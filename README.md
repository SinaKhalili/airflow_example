# Airflow

For this beginning example of using airflow, I decided to fetch some data from a free space api. I'd like to have a pipeline of three phases:

1. Print something to the terminal
2. Get some JSON data from an API call and store it as a JSON file
3. Translate that JSON into a csv file

To do this required three operators aranged in a linear dag.

### Set up
After importing the needed modules, I did some basic Airflow housekeeping.
```python
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
```


### Echo to terminal 
First we have the bash operator, this one this one just `echo`s something to the terminal, because saying blastoff is fun.
```python
task1 = BashOperator(
    task_id="blastoff",
    bash_command="echo '🚀 blastoff'",
    dag=dag,
)
```
### Fetch the data
Next we simply fetch our astronaut data with a simple API call
```python
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
```
Some improvements here could be to date the csv file name, or just pass it in as a parameter. 

### Parse into a csv
Finally we parse the data into a csv file
```python
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
```

### Conclusion
After defining a heirarchy,
```python
task1 >> task2 >> task3
```
We can simply run the airflow commands to check the functions
```bash
airflow test space_dag blastoff 2015-06-01

airflow test space_dag GET 2015-06-01

airflow test space_dag JSON 2015-06-01
```
Or we can `backfill` however in my example any backfilling is equivalent to doing it once. 
```bash
airflow backfill space_dag -s 2015-06-01 -e 2015-06-07
```

