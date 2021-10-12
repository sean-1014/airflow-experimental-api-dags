"""
# Trigger DAG through API

Trigger the api_task DAG.
"""

import base64
import logging
import re
import sys
import time
from datetime import datetime

import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

dag_name = "api_trigger_dag"


def trigger_dag():
    dag_name = "api_task"
    # Docker services within the same network can refer to each other by name
    # webserver here is the service name for the Airflow webserver
    url = "http://webserver:8080/api/experimental/dags/" + dag_name + "/dag_runs"
    # This is for demonstration purposes; never store passwords in plaintext
    creds = base64.b64encode(b"api_user:password").decode("utf-8")
    # Basic HTTP Auth is only okay to use if over HTTPS
    auth_header = {"Authorization": "Basic {}".format(creds)}
    payload = {
        "conf": {
            "query_field": "student",
            "query_value":"Alice"
        }
    }
    response = requests.post(url, json=payload, headers=auth_header)
    logging.info(response.text)
    exec_date = re.search('"execution_date":"(.*?)"', response.text).group(1)

    state = "running"
    while state == "running":
        time.sleep(5)
        response = requests.get("{}/{}".format(url, exec_date), headers=auth_header)
        state = re.search('"state":"(.*?)"', response.text).group(1)

    logging.info("DAG Trigger Status: {}".format(state.upper()))


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

    trigger = PythonOperator(
        task_id="trigger",
        python_callable=trigger_dag,
    )

    trigger
