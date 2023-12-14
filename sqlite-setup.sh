#!/bin/bash
cat sqlite-setup.sql | sqlite3 airflow.db
