import os
from datetime import datetime, timedelta, time
import glob
import duckdb
import pandas as pd

CURRENT_PATH = os.getcwd()
SOURCE_DIR = "problem_2_answer/data"
PATH: str = CURRENT_PATH+"/"+SOURCE_DIR
print('path: ',PATH)

def extract_previous_date(date: str):
    date = datetime.strptime(date, "%Y-%m-%d")
    yesterday_date = date - timedelta(days=1)
    return yesterday_date

def extract_parquet(forced_date: str, pipeline_type: int):
    previous_date = extract_previous_date(forced_date)
    year = previous_date.year
    month = previous_date.month if previous_date.month > 9 else "0"+str(previous_date.month)

    if pipeline_type == 1:
        df = pd.read_parquet(f"{PATH}/fhvhv_tripdata_{year}-{month}.parquet", columns=["request_datetime"])
    else:
        reg_path = sorted( glob.glob(f'{PATH}/*{year}*.parquet'))
        until_file_path = f'{PATH}/fhvhv_tripdata_{year}-{month}.parquet'
        index = 0
        fianl_file_path = []
        while reg_path[index] != until_file_path:
            fianl_file_path.append(reg_path[index])
            index += 1
            
        fianl_file_path.append(until_file_path)

        df_list = [pd.read_parquet(file, columns=["PULocationID", "request_datetime"]) for file in fianl_file_path]
        df = pd.concat(df_list, ignore_index=True)

    return df

def check_table_existed(database_name: str, table_name: str):
    conn = duckdb.connect(f"{database_name}.duckdb")
    result = conn.execute(f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name = '{table_name}'
    """).fetchall()
    conn.close()
    return 1 if len(result) > 0 else 0

def pipeline_1st(forced_date):
    df = extract_parquet(forced_date, 1)

    previous_date = extract_previous_date(forced_date)
    transformed_df = df[df["request_datetime"]==previous_date]

    now = datetime.now()
    hour = now.hour
    minute = now.minute
    second = now.second

    calculated_at = datetime.combine(previous_date.date(), time(hour, minute, second))

    transformed_data = {
        "transaction_date": [previous_date],
        "total_transactions": [transformed_df.shape[0]],
        "calculated_at": [calculated_at]
    }

    processed_df = pd.DataFrame(transformed_data)

    pk = "transaction_date"
    database_name = "processed"
    table_name = "daily_transaction"
    is_table_existed = check_table_existed(database_name, table_name)
    query_string = ""

    if is_table_existed:
        query_string = f"""
            DELETE FROM {table_name}
            WHERE {pk} = '{previous_date}';

            INSERT INTO {table_name} 
            SELECT *
            FROM processed_df;
        """
    else:
        query_string = f"""
            CREATE TABLE {table_name} (
                transaction_date DATE,
                total_transactions INT,
                calculated_at TIMESTAMP,
                PRIMARY KEY ({pk})
            );

            INSERT INTO {table_name}
            SELECT * FROM processed_df
        """

    conn = duckdb.connect(f"{database_name}.duckdb")

    conn.execute(query_string)

    conn.close()

    return 1

def pipeline_2nd(forced_date):
    df = extract_parquet(forced_date, 2)

    transformed_df = df[df["request_datetime"]<forced_date]
    transformed_df = transformed_df.groupby("PULocationID").size().reset_index(name="count")
    transformed_df.rename(columns={"PULocationID": "taxi_zone_id"}, inplace=True)
    transformed_df["rank"] = transformed_df["count"].rank(method="dense", ascending=False)
    transformed_df["rank"] = transformed_df["rank"].astype(int)
    transformed_df = transformed_df[transformed_df["rank"]<=5]

    forced_date = datetime.strptime(forced_date, "%Y-%m-%d")

    now = datetime.now()
    hour = now.hour
    minute = now.minute
    second = now.second

    calculated_at = datetime.combine(forced_date.date(), time(hour, minute, second))

    transformed_df["calculated_at"] = calculated_at

    processed_df = transformed_df[["taxi_zone_id", "rank", "calculated_at"]]
    
    pk = ["taxi_zone_id", "calculated_at"]
    pk_type = ["INT", "DATETIME"]
    database_name = "processed"
    table_name = "daily_topfive_taxi_zone"
    is_table_existed = check_table_existed(database_name, table_name)
    query_string = ""
    where_condition = " AND ".join(
        f"CAST(incoming.{column} AS DATE) = CAST(current.{column} AS DATE)" if pk_type[index] == "DATETIME" 
        else f"incoming.{column} = current.{column}"
        for index, column in enumerate(pk)
    )
    

    if is_table_existed:
        query_string = f"""
            DELETE FROM {table_name} current
            WHERE EXISTS (
                SELECT {', '.join(pk)}
                FROM processed_df incoming
                WHERE {where_condition}
            );

            INSERT INTO {table_name} 
            SELECT *
            FROM processed_df;
        """
    else:
        query_string = f"""
            CREATE TABLE {table_name} (
                taxi_zone_id INT,
                rank INT,
                calculated_at TIMESTAMP,
                PRIMARY KEY ({','.join(pk)})
            );

            INSERT INTO {table_name}
            SELECT * FROM processed_df
        """

    conn = duckdb.connect(f"{database_name}.duckdb")

    conn.execute(query_string)

    conn.close()
    return 1