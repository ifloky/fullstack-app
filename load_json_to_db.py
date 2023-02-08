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
    print(file_name)
    json_data = await load_json_data(file_name)
    conn = psycopg2.connect(dbname=credentials.test_name, user=credentials.test_username,
                            password=credentials.test_password, host=credentials.test_host)
    cur = conn.cursor()
    for data in json_data:
        cur.execute(
            'INSERT INTO public.rounds (round_id, account_id, game_id, created_at) VALUES (%s, %s, %s, %s)',
            (data['round_id'], data['account_id'], data['game_id'], data['created_at']))
    conn.commit()
    cur.close()
    conn.close()


async def main():
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_job_time = time.perf_counter()
    print(f"Start script at {current_date}")
    dir_path = 'N93_20230206T165940'
    file_list = os.listdir(dir_path)
    tasks = [asyncio.create_task(save_data_to_db(f'{dir_path}/{file_name}')) for file_name in file_list]
    await asyncio.gather(*tasks)

    stop_job_time = time.perf_counter()
    working_time = stop_job_time - start_job_time

    print(f"Script finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Working time:", str(timedelta(seconds=working_time)))
    print(f'Время выполнения: {time.perf_counter() - start_job_time:0.4f} seconds')
    from memory_profiler import memory_usage
    print("Затрачено памяти:", (memory_usage())[-1], "Mb")


if __name__ == '__main__':
    asyncio.run(main())
