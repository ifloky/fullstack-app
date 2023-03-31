import psycopg2
import requests
from urllib3.exceptions import ConnectTimeoutError

import credentials
import time
import asyncio

from datetime import datetime, timedelta
from memory_profiler import memory_usage


async def db_connect():
    """ Эта функция подключения к базе данных """
    conn = psycopg2.connect(
        host=credentials.db_host,
        database=credentials.db_name,
        user=credentials.db_username,
        password=credentials.db_password,
        connect_timeout=3
    )
    cursor = conn.cursor()
    return cursor


async def get_rounds_id_from_db():
    """ Эта функция получает данные из базы данных """
    cursor = await db_connect()
    cursor.execute("""
                    SELECT *
                    FROM public.main_nocloserounds
                    WHERE game_id != 2 AND cmd is null
                    ORDER BY round_id ASC
                    """)
    rounds_id = cursor.fetchall()
    return rounds_id


async def get_round_data_from_skks(skks_host, transaction_id):
    """ Эта функция получает данные из SKKS """
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'User-Agent': 'PostmanRuntime/7.29.2',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    body = {
        "_cmd_": "Transaction/Read",
        "tr_id": transaction_id
    }

    try:
        response = requests.post(
            url=skks_host,
            headers=headers,
            json=body,
        )

        status = response.json()['_status_']

        if status != 0:
            cmd = 'Раунд не найден'
            amount = ''
            return cmd, amount
        else:
            cmd = response.json()['cmd']
            amount = response.json()['amount']
            return cmd, amount
    except (ConnectionError, ConnectTimeoutError) as e:
        print(e)
        await asyncio.sleep(5)
        response = requests.post(
            url=skks_host,
            headers=headers,
            json=body,
        )

        status = response.json()['_status_']

        if status != 0:
            cmd = 'Раунд не найден'
            amount = ''
            return cmd, amount
        else:
            cmd = response.json()['cmd']
            amount = response.json()['amount']
            return cmd, amount


async def update_round_data_to_db(db_name, round_id, cmd, amount):
    """ Эта функция обновляет данные в базе данных """
    cursor = await db_connect()
    cursor.execute(f"""
                    UPDATE {db_name}
                    SET cmd = {cmd}, amount = {amount}
                    WHERE round_id = {round_id}
                    """)
    cursor.connection.commit()
    cursor.close()


async def main():
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_job_time = time.perf_counter()
    print(f"Start script at {current_date}")

    skks_host = f'{credentials.skks_host}/Transaction/Read'
    db_name = 'public.main_nocloserounds'

    rounds_id = await get_rounds_id_from_db()
    count = 1
    for round_id in rounds_id:
        transaction_id = round_id[0]
        response_data = await get_round_data_from_skks(skks_host, transaction_id)
        await update_round_data_to_db(db_name, transaction_id, response_data[0], response_data[1])
        print(count, transaction_id, '-', response_data[0], int(response_data[1] or 0) / 100, 'BYN')
        count = count + 1

    stop_job_time = time.perf_counter()
    working_time = stop_job_time - start_job_time

    print(f"Script finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Время выполнения:", str(timedelta(seconds=working_time)))
    print("Затрачено памяти:", (memory_usage())[-1], "Mb")


if __name__ == '__main__':
    asyncio.run(main())
