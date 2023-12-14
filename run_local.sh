#!/bin/bash

# export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////workspaces/andy-sprague-take-home-exercise/airflow.db
# export AIRFLOW_HOME="/workspaces/andy-sprague-take-home-exercise"
# export AIRFLOW__CORE__LOAD_EXAMPLES="False"
# export AIRFLOW__CORE__DAGS_FOLDER="/workspaces/andy-sprague-take-home-exercise/src/dags"
# export AIRFLOW__CORE__EXECUTOR="SequentialExecutor"

airflow db migrate

airflow users create \
    --username admin \
    --password admin \
    --firstname Andy \
    --lastname Sprague \
    --role Admin \
    --email andy.sprague44@gmail.com

airflow webserver --port 8080

# airflow scheduler
