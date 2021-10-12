# Airflow Experimental API DAGs

Airflow DAGs that demonstrate how to interact with the Experimental Airflow REST API.

### `api_task_DAG.py`
This DAG contains code for querying from some dummy data and checking whether the query parameters passed through the DAG run `conf` correspond to any data that can be found in the table. The DAG contains two Airflow tasks which communicate via XComs. The first task runs an input verification function to check whether the inputs to `conf` are valid values. The second task performs the actual query on the table.

#### Inputs
- `query_field` - The column to search from
- `query_value` - The value to search for in `query_field`

#### Table
| Student | Class | Grade |
|---|---|---|
| Alice | A | B- |
| Bob | A | B+ |
| Connor | B | A- |
| Daniel | B | C+ |

### `api_trigger_DAG.py`
This DAG contains code for triggering the `api_task_DAG` to run through the Airflow API. This DAG is for demonstration purposes only. There's little reason to use the Airflow API through a DAG running on that same server. But code here can be nearly identical to how a Python script would call the API from outside.

This code triggers the `api_task_DAG` through the API and repeatedly makes GET requests to the Airflow server to watch the status of the triggered DAG run. When the run has either failed or succeeded, this DAG outputs the result to log and finishes running.

#### Implementation Notes
1. This DAG will succeed assuming that the Airflow server that hosts `api_task_DAG` allows API calls and authenticates using `auth_backend` and has an API user called `api_user` whose password is `password`.
2. The authentication method used here for simplicity's sake is HTTP Basic Auth, which is not secure as the credentials are passed over the connection unencrypted. This is not safe to use when the Airflow server does not use HTTPS.
3. Since this DAG runs from within a Dockerized Airflow instance, the url in the POST request refers to the name of the `webserver` Docker container. This will obviously change if calling the API from outside the Dockerized Airflow environment.
