import asyncio
import time
import json
import os
import psycopg2
from mysite import credentials
from datetime import datetime, timedelta
from memory_profiler import memory_usage


async def save_data_to_db(file_name, conn, cur, db_name):
    start_job_time = time.perf_counter()

    with open(file_name) as my_file:
        data = json.load(my_file)

        query_sql = f""" insert into {db_name}
            select * from json_populate_recordset(NULL::{db_name}, %s) """
        cur.execute(query_sql, (json.dumps(data),))

    conn.commit()
    stop_job_time = time.perf_counter()
    working_time = stop_job_time - start_job_time
    print(file_name, "Время сохранения в ДБ:", str(timedelta(seconds=working_time)))


def find_dir_by_mask(mask):
    catalogs = [d for d in os.listdir(os.getcwd()) if os.path.isdir(d) and d.startswith(mask)]
    catalogs.sort()
    return catalogs[-1]


def clear_data(db_name):
    connection = psycopg2.connect(database=credentials.db_name,
                                  user=credentials.db_username,
                                  password=credentials.db_password,
                                  host=credentials.db_host,
                                  port=credentials.db_port,
                                  )
    cursor = connection.cursor()
    cursor.execute(
        f"TRUNCATE TABLE {db_name} RESTART IDENTITY CASCADE;")
    print(cursor.statusmessage)
    connection.commit()
    connection.close()


async def main():
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_job_time = time.perf_counter()
    print(f"Start script at {current_date}")

    conn = psycopg2.connect(dbname=credentials.db_name, user=credentials.db_username,
                            password=credentials.db_password, host=credentials.db_host)
    cur = conn.cursor()

    db_name = 'public.main_nocloserounds'

    clear_data(db_name)

    dir_path = find_dir_by_mask('N93_')
    file_list = os.listdir(dir_path)
    tasks = [asyncio.create_task(
        save_data_to_db(f'{dir_path}/{file_name}', conn, cur, db_name)) for file_name in file_list]
    await asyncio.gather(*tasks)

    cur.close()
    conn.close()

    stop_job_time = time.perf_counter()
    working_time = stop_job_time - start_job_time

    print(f"Script finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Время выполнения:", str(timedelta(seconds=working_time)))
    print("Затрачено памяти:", (memory_usage())[-1], "Mb")


if __name__ == '__main__':
    asyncio.run(main())
