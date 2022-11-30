import psycopg2

from credentials import cc_db_host, cc_db_port, cc_db_name, cc_db_username, cc_db_password
from datetime import timedelta, datetime
from mysql.connector import Error, connect

import pandas as pd
import time

from mysite import credentials


def get_mysql_connection():
    print('Connecting to MySQL database...')
    try:
        connection = connect(host=cc_db_host,
                             port=cc_db_port,
                             database=cc_db_name,
                             user=cc_db_username,
                             password=cc_db_password)
        return connection
    except Error as e:
        print(e)


def create_df(call_date='2022-11-01'):
    current_date = datetime.now().strftime("%Y-%m-%d")
    print('Creating DataFrame...')
    df = []
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()
        query = (F'''
                SELECT CallDateTime, Type, Operator, Client FROM asterisk.CallsCountAll
                WHERE TYPE = 'Исходящий' AND CallDate between '{call_date}' and '{current_date}'
                ''')
        cursor.execute(query)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=[c[0] for c in cursor.description])
        cursor.close()
        connection.close()
        # print('Загружено из базы АТС:', str(len(df)), 'записей')
    except Error as e:
        print(e)
    return df


def load_phone_number_from_db(db_name):
    """ This function get data from callscheck db table and return it as list of dicts """
    cursor, connection = None, None

    phones = []

    sql_query = (f'''
                SELECT client_phone
                FROM {db_name}
                WHERE call_date is null AND call_result != 'есть фото' AND call_result != 'номер не РБ' 
                ''')

    try:
        connection = psycopg2.connect(database=credentials.db_name,
                                      user=credentials.db_username,
                                      password=credentials.db_password,
                                      host=credentials.db_host,
                                      port=credentials.db_port,
                                      )

        cursor = connection.cursor()
        cursor.execute(sql_query)

        phone_list = cursor.fetchall()

        for phone in phone_list:
            if phone is not None:
                phone = str(phone).replace(' ', '').replace('-', '').replace('(', '')
                phone = phone.replace(')', '').replace("'", "").split(',')[0]
                phones.append(phone)
            else:
                continue
        if db_name == 'public.main_callscheck':
            database_name = 'Call Centre'
        else:
            database_name = 'CRM'
        print(f'Loading phone numbers from db {database_name}:', len(phones), 'records.')

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgresSQL", error)

    finally:
        if connection:
            cursor.close()
            connection.close()

    return phones


def check_call(phone_number, df, db_name):
    for index, row in df.iterrows():
        if row['client'] == phone_number:
            check = row['client'], row['CallDateTime'].strftime("%Y-%m-%d %H:%M:%S")
            call_date_time = row['CallDateTime'].strftime("%Y-%m-%d %H:%M:%S")
            client_number = row['client']
            check = str(check).replace('(', '').replace(')', '').replace("'", '')
            update_call_date_in_db(client_number, call_date_time, db_name)
            # print(check)
            print(client_number, call_date_time)
            return check
    print(str(phone_number) + ', ' + 'No Calls')
    return str(phone_number)+', ' + 'No Calls'


def update_call_date_in_db(phone_number, call_date_time, db_name):
    cursor, connection = None, None

    sql_query = (f'''
                UPDATE {db_name}
                SET call_date = '{call_date_time}'
                WHERE client_phone = '{phone_number}'
                ''')

    try:
        connection = psycopg2.connect(database=credentials.db_name,
                                      user=credentials.db_username,
                                      password=credentials.db_password,
                                      host=credentials.db_host,
                                      port=credentials.db_port,
                                      )

        cursor = connection.cursor()
        cursor.execute(sql_query)
        connection.commit()
        print('Call Date Updated to client number:', phone_number)

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgresSQL", error)

    finally:
        if connection:
            cursor.close()
            connection.close()


def get_date_15_days_ago():
    date_30_days_ago = datetime.now() - timedelta(days=15)
    return date_30_days_ago.strftime('%Y-%m-%d')


def main():
    cc_db = 'public.main_callscheck'
    crm_db = 'public.main_crmcheck'
    date_range = get_date_15_days_ago()
    start_job_time = time.perf_counter()
    data = []
    df = create_df(date_range)
    cc_phones = load_phone_number_from_db(cc_db)
    crm_phones = load_phone_number_from_db(crm_db)

    phone_numbers = cc_phones + crm_phones

    for cc_phone in cc_phones:
        data.append(check_call(cc_phone, df, cc_db))

    for crm_phone in crm_phones:
        data.append(check_call(crm_phone, df, crm_db))

    stop_job_time = time.perf_counter()
    working_time = stop_job_time - start_job_time

    print('Задание выполненно в:', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print('Загружено из базы АТС:', str(len(df)), 'записей')
    print('Загружено из базы Отчетов:', len(phone_numbers), 'записей')
    print("Проверено и сохранено:", len(data), "номеров")
    print("Затрачено времени:", str(timedelta(seconds=working_time)))
    print(f'Время выполнения: {time.perf_counter() - start_job_time:0.4f} seconds')
    print('\n')


if __name__ == '__main__':
    main()
