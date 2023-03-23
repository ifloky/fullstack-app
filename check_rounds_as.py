import psycopg2
import requests
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
                    -- WHERE game_id != 2 AND cmd is null
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
        if cmd == 6:
            cmd = "Выиграшная ставка"
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

    # skks_host = f'{credentials.skks_host}/Transaction/Read'
    skks_host = f'{credentials.skks_test_host}/Transaction/Read'
    db_name = 'public.main_nocloserounds'

    # rounds_id = await get_rounds_id_from_db()
    rounds_id = [(116383500752,), (116383797839,), (116383984010,), (116383954558,), (116383978489,), (116383948297,), (116383973040,),
                 (116382948129,), (116382928739,), (116382532792,), (116382718187,), (116382710910,), (116382703530,), (116382115521,),
                 (116382136807,), (116382129460,), (116382038443,), (116382101788,), (116382074123,), (116382067455,), (116382094552,),
                 (116381804736,), (116382059695,), (116381898981,), (116381841829,), (116381834855,), (116380856639,), (116380760644,),
                 (116380753451,), (116380492875,), (116380520863,), (116380514702,), (116380544630,), (116380502503,), (116380538811,),
                 (116380431335,), (116379964460,), (116379941415,), (116379769448,)]
    count = 1
    for round_id in rounds_id:
        transaction_id = round_id[0]
        response_data = await get_round_data_from_skks(skks_host, transaction_id)
        # await update_round_data_to_db(db_name, transaction_id, response_data[0], response_data[1])
        print(count, transaction_id, '-', response_data[0], int(response_data[1] or 0) / 100, 'BYN')
        count = count + 1

    stop_job_time = time.perf_counter()
    working_time = stop_job_time - start_job_time

    print(f"Script finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Время выполнения:", str(timedelta(seconds=working_time)))
    print("Затрачено памяти:", (memory_usage())[-1], "Mb")


if __name__ == '__main__':
    asyncio.run(main())
