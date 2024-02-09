import psycopg2
import pandas as pd
import time

from datetime import timedelta, datetime
from psycopg2 import Error

from mysite import credentials


def get_fd_postgres_connection():
    """ This function create connection to Postgres DB """
    try:
        connection = psycopg2.connect(database=credentials.fd_db_name,
                                      user=credentials.fd_db_username,
                                      password=credentials.fd_db_password,
                                      host=credentials.fd_db_host,
                                      port=credentials.fd_db_port,
                                      )
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
    date_range = datetime.now() - timedelta(days=delta)
    return date_range


def create_df(data_range):
    """ This function create dataframe from DB table """
    print('Connecting to Deposit database...')
    print('Creating DataFrame...')
    cursor, connection = None, None
    df = []

    sql_query = (f'''
                SELECT client_id, amount, transaction_date
                FROM public.v_client_deposit
                WHERE transaction_date > '{data_range}'
                ORDER BY transaction_date DESC
                ''')

    try:
        connection = get_fd_postgres_connection()
        cursor = connection.cursor()
        cursor.execute(sql_query)

        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['client_id', 'amount', 'date'])
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgresSQL", error)

    finally:
        if connection:
            cursor.close()
            connection.close()
    return df


def load_client_id_from_db(date_range):

    print('Connecting to Postgres database...')
    cursor, connection = None, None

    clients = []

    sql_query = (f'''
                SELECT client_id
                FROM public.main_crmcheck
                WHERE first_deposit_date is Null AND upload_date > '{date_range}'
                ORDER BY upload_date DESC
                ''')

    try:
        connection = get_postgres_connection()

        cursor = connection.cursor()
        cursor.execute(sql_query)

        client_list = cursor.fetchall()
        for client in client_list:
            clients.append(client[0])

        print(f'Loading no deposit clients from {date_range}:', len(clients), 'records.')

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgresSQL", error)

    finally:
        if connection:
            cursor.close()
            connection.close()

    return clients


def get_deposit_amount_and_date_in_df(df, client):
    try:
        deposit = df.loc[df['client_id'] == client, 'amount'].iloc[0]
        date = df.loc[df['client_id'] == client, 'date'].iloc[0]
        return str(deposit) + ', ' + str(date)
    except IndexError:
        return 'No Deposit' + ', ' + 'No Date'


def update_call_date_in_db(client, db_name, deposit, date):
    cursor, connection = None, None
    sql_query = (f'''
                UPDATE {db_name}
                SET first_deposit_amount = {deposit}, first_deposit_date = '{date}'
                WHERE client_id = '{client}'
                ''')

    try:
        connection = get_postgres_connection()

        cursor = connection.cursor()
        cursor.execute(sql_query)
        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgresSQL", error)

    finally:
        if connection:
            cursor.close()
            connection.close()


def check_deposit(client, df, db_name):
    for index, row in df.iterrows():
        if row['client_id'] == client:
            deposit = get_deposit_amount_and_date_in_df(df, client)
            print(str(client) + ', ' + deposit)
            update_call_date_in_db(client, db_name, deposit.split(',')[0], deposit.split(',')[1])
            return deposit


def main():
    data = []
    db_name = 'public.main_crmcheck'
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Start script at {current_date}")
    date_range = get_date_of_time_delta(32).strftime('%Y-%m-%d')
    print('Date range:', date_range, 'to', datetime.now().strftime('%Y-%m-%d'))
    start_job_time = time.perf_counter()

    df = create_df(date_range)
    print('DataFrame created successfully...')
    clients = load_client_id_from_db(date_range)
    print('Clients loaded successfully...')

    for client in clients:
        dep = check_deposit(client, df, db_name)
        if dep is not None:
            data.append([client, dep])
        else:
            continue

    stop_job_time = time.perf_counter()
    working_time = stop_job_time - start_job_time

    print('Задание выполнено в:', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print('Загружено из базы Депозитов:', len(df), 'записей')
    print('Загружено из базы Бездепозитников:', len(clients), 'записей')
    print("Проверено и сохранено:", len(data), "клиентов")
    print("Затрачено времени:", str(timedelta(seconds=working_time)))
    # measure memory after loading
    from memory_profiler import memory_usage
    print("Затрачено памяти:", (memory_usage())[-1], "Mb")
    print('\n')


if __name__ == '__main__':
    main()