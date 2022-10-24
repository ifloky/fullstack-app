from credentials import cc_db_host, cc_db_port, cc_db_name, cc_db_username, cc_db_password

from openpyxl import load_workbook
from mysql.connector import Error, connect


def get_clients_numbers_list():
    wb = load_workbook('./book2.xlsx')
    sheet = wb.get_sheet_by_name('по фильтру')
    for cellObj in sheet['D3':'D5']:
        for cell in cellObj:
            if cell.value is not None:
                phone_number = cell.value
                phone_number = str(phone_number)
                phone_number = phone_number.replace(' ', '')
                phone_number = phone_number.replace('-', '')
                phone_number = phone_number.replace('(', '')
                phone_number = phone_number.replace(')', '')
                phone_number = "+" + phone_number
                print(phone_number, '-', check_call(phone_number))
            else:
                continue


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


def check_call(client_number):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = (F'''
                SELECT * FROM asterisk.CallsCountAll
                WHERE TYPE = 'Исходящий' AND client = '{client_number}' 
                LIMIT 10
                ''')
        cursor.execute(query)
        data = f'{client_number} - {cursor.fetchall()[0][0]}'
        cursor.close()
        connection.close()
    except IndexError:
        data = f'{client_number} - No Calls'
    return data


def main():
    data = []

    wb = load_workbook('./book2.xlsx')
    sheet = wb['по фильтру']
    for cellObj in sheet['D3':'D240']:
        for cell in cellObj:
            if cell.value is not None:
                phone_number = cell.value
                phone_number = str(phone_number)
                phone_number = phone_number.replace(' ', '')
                phone_number = phone_number.replace('-', '')
                phone_number = phone_number.replace('(', '')
                phone_number = phone_number.replace(')', '')
                phone_number = "+" + phone_number
                print("Check:", phone_number)
                data.append(check_call(phone_number))
            else:
                continue
    print(data)

    file = open('result.txt', 'w')
    for item in data:
        file.write("%s \n" % item)
    file.close()


if __name__ == '__main__':
    main()
