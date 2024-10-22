# Command Line

## To build a Python virtual environment
`python[version] -m venv .venv`

## To acivate/deactivate the virtual environment
`source .venv/bin/activate` --> MacOS
`airflow-env\Scripts\activate` --> Windows

`deactivate`

## To set the Airflow home directory
`export AIRFLOW_HOME=$(pwd)/[airflow_home]`

# Airflow

## To list error dags
`airflow dags list-import-errors`