from credentials import cc_db_host, cc_db_port, cc_db_name, cc_db_username, cc_db_password
from datetime import timedelta, datetime
from mysql.connector import Error, connect

import pandas as pd

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


def create_df(call_date, phone_number):
    current_date = datetime.now().strftime("%Y-%m-%d")
    print('Creating DataFrame...')
    df = []
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()
        query = (F'''
                SELECT CallDateTime, Type, Operator, Client FROM asterisk.CallsCountAll
                WHERE TYPE = 'Исходящий' 
                AND CallDate between '{call_date}' and '{current_date}'
                AND Client = '{phone_number}'
                ''')
        cursor.execute(query)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=[c[0] for c in cursor.description])
        cursor.close()
        connection.close()
    except Error as e:
        print(e)
    return df


def main():
    call_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    phone_number = '+375291926835'
    df = create_df(call_date, phone_number)
    print(df)


if __name__ == "__main__":
    main()
