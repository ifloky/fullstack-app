import asyncio
import json
import os
import psycopg2

from mysite import credentials


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
            'INSERT INTO public.rounds2 (round_id, account_id, game_id, created_at) VALUES (%s, %s, %s, %s)',
            (data['round_id'], data['account_id'], data['game_id'], data['created_at']))
    conn.commit()
    cur.close()
    conn.close()


async def main():
    dir_path = 'N93_20230202T160053'
    file_list = os.listdir(dir_path)
    tasks = [asyncio.create_task(save_data_to_db(f'{dir_path}/{file_name}')) for file_name in file_list]
    await asyncio.gather(*tasks)


asyncio.run(main())
