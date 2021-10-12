"""
# API Task

This DAG contains some dummy data that can be queried

Columns: student, class, grade

A simple function tells whether the query returned any
results or not.
"""

import logging
from datetime import datetime

import pandas as pd
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

dag_name = "api_task"

data = pd.DataFrame(
    {
        'student': ['Alice', 'Bob', 'Connor', 'Daniel'],
        'class': ['A', 'A', 'B', 'B'], 
        'grade': ['B-', 'B+', 'A-', 'C+']
    }
)

def check_query_params(task_instance, **kwargs):
    # Get params from request body
    query_field = kwargs["dag_run"].conf.get("query_field")
    query_value = kwargs["dag_run"].conf.get("query_value")

    # Validation
    if query_field not in ["student", "class", "grade"]:
        raise ValueError("Unrecognized field.")
    if not isinstance(query_value, str):
        raise ValueError("Invalid data type. Must be string.")

    logging.info(f"Query Field: {query_field}")
    logging.info(f"Query Value: {query_value}")
    task_instance.xcom_push(key="query_field", value=query_field)
    task_instance.xcom_push(key="query_value", value=query_value)


def query(query_field, query_value, **kwargs):
    if len(data[data[query_field]==query_value]):
        logging.info("Found")
    else:
        logging.info("Not Found.")


default_args = {
    "owner": "Sean Sy",
    "depends_on_past": False,
    "start_date": datetime(2021, 1, 1),
    "email": ["seannevintsy@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
}

with DAG(
    dag_name, default_args=default_args, schedule_interval=None
) as dag:
    dag.doc_md = __doc__

    check_query_params = PythonOperator(
        task_id="check_query_params",
        python_callable=check_query_params,
        provide_context=True,
    )

    query_xcom = (
        "{{{{ task_instance.xcom_pull(dag_id='"
        + dag_name
        + "', task_ids='check_query_params', key='{}') }}}}"
    )

    query = PythonOperator(
        task_id="query",
        python_callable=query,
        provide_context=True,
        op_kwargs={
            "query_field": query_xcom.format("query_field"),
            "query_value": query_xcom.format("query_value")
        }
    )

    check_query_params >> query
