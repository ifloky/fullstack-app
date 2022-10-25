from credentials import cc_db_host, cc_db_port, cc_db_name, cc_db_username, cc_db_password

from openpyxl import load_workbook
from mysql.connector import Error, connect

import pandas as pd


def get_connection():
    try:
        connection = connect(host=cc_db_host,
                             port=cc_db_port,
                             database=cc_db_name,
                             user=cc_db_username,
                             password=cc_db_password)
        return connection
    except Error as e:
        print(e)


def load_data():
    df = []
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = (F'''
                SELECT CallDateTime, Type, Operator, Client FROM asterisk.CallsCountAll
                WHERE TYPE = 'Исходящий' AND CallDate >= '2022-10-01'
                ''')
        cursor.execute(query)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=[c[0] for c in cursor.description])
        cursor.close()
        connection.close()
    except Error as e:
        print(e)
    return df


def check_call(phone_number, df):
    for index, row in df.iterrows():
        if row['client'] == phone_number:
            check = row['client'], row['CallDateTime'].strftime("%Y-%m-%d %H:%M:%S")
            check = str(check)
            check = check.replace('(', '').replace(')', '').replace("'", '')
            return check
        else:
            continue
    return str(phone_number)+', ' + 'No Calls'


def main():
    data = []
    wb = load_workbook('./book.xlsx')
    df = load_data()
    print(f'Загружено из базы данных:', str(len(df)), 'записей')
    sheet = wb['фильтр']
    print(f'Загружено из файла:', sheet.max_row, 'записей')
    max_row = str('E') + str(sheet.max_row)
    for cellObj in sheet['E3':max_row]:
        for cell in cellObj:
            if cell.value is not None:
                phone_number = cell.value
                phone_number = str(phone_number)
                phone_number = phone_number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                phone_number = "+" + phone_number
                # print("Check phone number:", phone_number)
                data.append(check_call(phone_number, df))
                print(data[-1])
            else:
                continue

    file = open('result.txt', 'w')
    for item in data:
        file.write("%s \n" % item)
    file.close()

    print("Проверено и сохранено:", len(data), "номеров")


if __name__ == '__main__':
    main()
