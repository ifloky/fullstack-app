import asyncio
import time
import json
import os
import psycopg2
from mysite import credentials
from datetime import datetime, timedelta


async def load_json_data(file_name):
    with open(file_name, 'r') as f:
        json_data = json.load(f)
    return json_data


async def save_data_to_db(file_name):
    start_job_time = time.perf_counter()
    # json_data = await load_json_data(file_name)
    conn = psycopg2.connect(dbname=credentials.test_name, user=credentials.test_username,
                            password=credentials.test_password, host=credentials.test_host)

    with conn.cursor() as cur:
        with open(file_name) as my_file:
            data = json.load(my_file)

            query_sql = """ insert into public.rounds_clear
                select * from json_populate_recordset(NULL::public.rounds_clear, %s) """
            cur.execute(query_sql, (json.dumps(data),))

    conn.commit()
    cur.close()
    conn.close()
    stop_job_time = time.perf_counter()
    working_time = stop_job_time - start_job_time
    print(file_name, "Время сохранения в ДБ:", str(timedelta(seconds=working_time)))


def find_dir_by_mask(mask):
    catalogs = [d for d in os.listdir(os.getcwd()) if os.path.isdir(d) and d.startswith(mask)]
    catalogs.sort()
    return catalogs[-1]


async def main():
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_job_time = time.perf_counter()
    print(f"Start script at {current_date}")
    dir_path = find_dir_by_mask('N93_')
    file_list = os.listdir(dir_path)
    tasks = [asyncio.create_task(save_data_to_db(f'{dir_path}/{file_name}')) for file_name in file_list]
    await asyncio.gather(*tasks)

    stop_job_time = time.perf_counter()
    working_time = stop_job_time - start_job_time

    print(f"Script finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Время выполнения:", str(timedelta(seconds=working_time)))
    from memory_profiler import memory_usage
    print("Затрачено памяти:", (memory_usage())[-1], "Mb")


if __name__ == '__main__':
    asyncio.run(main())
