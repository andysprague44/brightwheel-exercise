#!/bin/bash

export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////workspaces/andy-sprague-take-home-exercise/airflow.db

airflow db migrate

airflow users create \
    --username admin \
    --password 3zSR6dFRhFbmYvYs \
    --firstname Andy \
    --lastname Sprague \
    --role Admin \
    --email andy.sprague44@gmail.com

airflow webserver --port 8080

airflow scheduler
