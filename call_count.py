# pip install polars-lts-cpu

import psycopg2
import polars as pl
import time

from credentials import cc_db_host, cc_db_port, cc_db_name, cc_db_username, cc_db_password
from datetime import timedelta, datetime
from mysql.connector import Error, connect
from mysite import credentials


def get_mysql_connection():
    """ This function create connection to MySQL DB """
    try:
        connection = connect(host=cc_db_host,
                             port=cc_db_port,
                             database=cc_db_name,
                             user=cc_db_username,
                             password=cc_db_password)
        return connection
    except Error as e:
        print(e)


def get_postgres_connection():
    """ This function create connection to Postgres DB """
    try:
        connection = psycopg2.connect(database=credentials.db_name,
                                      user=credentials.db_username,
                                      password=credentials.db_password,
                                      host=credentials.db_host,
                                      port=credentials.db_port,
                                      )
        return connection
    except Error as e:
        print(e)


def get_date_of_time_delta(delta):
    date_15_days_ago = datetime.now() - timedelta(days=delta)
    return date_15_days_ago


def create_df(call_date):
    """ This function create dataframe from DB table """
    current_date = datetime.now().strftime("%Y-%m-%d")
    print('Connecting to MySQL database...')
    print('Creating DataFrame...')
    df = []
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()
        query = (F'''
                SELECT CallDateTime, Client FROM asterisk.CallsCountAll
                WHERE TYPE = 'Исходящий' AND CallDate between '{call_date}' AND '{current_date}'
                                         AND client NOT LIKE '%+375+375+%'
                ''')
        cursor.execute(query)
        data = cursor.fetchall()
        # df = pl.DataFrame(data, columns=[c[0] for c in cursor.description])
        df = pl.DataFrame(data, schema=[c[0] for c in cursor.description])
        cursor.close()
        connection.close()
    except Error as e:
        print(e)
    return df


def load_phone_number_from_db(db_name, date_range):
    """ This function get data from callscheck db table and return it as list of dicts """
    print('Connecting to Postgres database...')
    cursor, connection = None, None
    current_date = datetime.now().strftime("%Y-%m-%d")

    phones = []

    sql_query = (f'''
                SELECT client_phone
                FROM {db_name}
                WHERE (call_date between '{date_range}' AND '{current_date}' AND calls_count is null) 
                   OR (call_date between '{date_range}' AND '{current_date}' AND calls_count <= 1)
                ORDER BY call_date ASC
                ''')

    try:
        connection = get_postgres_connection()

        cursor = connection.cursor()
        cursor.execute(sql_query)

        phone_list = cursor.fetchall()

        for phone in phone_list:
            if phone is not None:
                phones.append(phone[0])
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


def count_calls_in_df(df, phone_number):
    count = 0
    for index, row in df.iter_rows():
        if row == phone_number:
            count += 1
    # print(str(phone_number) + ', ' + str(count))
    return count


def check_calls_count(phone_number, df, db_name):
    for index, row in df.iter_rows():
        if row == phone_number:
            count_calls = count_calls_in_df(df, phone_number)
            update_call_date_in_db(phone_number, db_name, count_calls)
            return count_calls
    print(str(phone_number) + ', ' + 'No Calls')
    return str(phone_number)+', ' + 'No Calls'


def update_call_date_in_db(phone_number, db_name, calls):
    cursor, connection = None, None
    sql_query = (f'''
                UPDATE {db_name}
                SET calls_count = {calls}
                WHERE client_phone = '{phone_number}'
                ''')

    try:
        connection = get_postgres_connection()

        cursor = connection.cursor()
        cursor.execute(sql_query)
        connection.commit()
        # print('Calls count updated to Client number:', phone_number, 'Total call count:', calls)

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgresSQL", error)

    finally:
        if connection:
            cursor.close()
            connection.close()


def main():
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Start script at {current_date}")
    cc_db = 'public.main_callscheck'
    crm_db = 'public.main_crmcheck'
    date_range = get_date_of_time_delta(32).strftime('%Y-%m-%d')
    print('Date range:', date_range, 'to', datetime.now().strftime('%Y-%m-%d'))
    start_job_time = time.perf_counter()
    data = []
    df = create_df(date_range)
    cc_phones = load_phone_number_from_db(cc_db, date_range)
    crm_phones = load_phone_number_from_db(crm_db, date_range)

    phone_numbers = cc_phones + crm_phones

    for cc_phone in cc_phones:
        data.append(check_calls_count(cc_phone, df, cc_db))

    for crm_phone in crm_phones:
        data.append(check_calls_count(crm_phone, df, crm_db))

    stop_job_time = time.perf_counter()
    working_time = stop_job_time - start_job_time

    print('Задание выполнено в:', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print('Загружено из базы АТС:', str(len(df)), 'записей')
    print('Загружено из базы Отчетов:', len(phone_numbers), 'записей')
    print("Проверено и сохранено:", len(data), "номеров")
    print("Затрачено времени:", str(timedelta(seconds=working_time)))
    # measure memory after loading
    from memory_profiler import memory_usage
    print("Затрачено памяти:", (memory_usage())[-1], "Mb")
    print('\n')


if __name__ == '__main__':
    main()
