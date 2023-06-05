import time
import xmltodict
import requests
import psycopg2

from datetime import timedelta, datetime
from credentials import backoffice_authentication, backoffice_cookie
from credentials import db_name, db_username, db_password, db_host, db_port


def get_postgres_connection():
    """ This function create connection to Postgres DB """
    try:
        connection = psycopg2.connect(user=db_username,
                                      password=db_password,
                                      host=db_host,
                                      port=db_port,
                                      database=db_name)
        return connection
    except Exception as e:
        print(e)


def xml_to_dict(element):
    result = {}
    for child in element:
        if len(child) == 0:
            result[child.tag] = child.text
        else:
            result[child.tag] = xml_to_dict(child)
    return result


def set_headers():
    """ Задаем параметры заголовков для веб запросов.
     Setting header parameters for web requests. """

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3;q=0.9",

        "Authentication": backoffice_authentication,

        "Cookie": backoffice_cookie,

        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/107.0.0.0 Safari/537.36 "
    }

    return headers


def set_params(client_id):
    """ Задаем параметры для запроса.
     Setting parameters for the request. """

    params = {
        'id': client_id,
    }

    return params


def get_data(url, params):
    """ Получаем html код страницы.
     Getting html code of the page. """

    r = requests.get(url, headers=set_headers(), params=params)

    response_bytes = r.content

    # Декодируем байты в строку
    response_str = response_bytes.decode('utf-8')
    # print(response_str)

    parsed_data = {}
    try:
        response_dict = xmltodict.parse(response_str)
        parsed_data = response_dict
    except Exception as e:
        print(e)

    try:
        client_first_deposit_date =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:FirstDepositTime']['d3p1:DateTime']).replace("{'@i:nil': 'true'}", 'Нет данных')
        print('Обновляется дата первого депозита клиента:',params['id'], client_first_deposit_date.split('T')[0])
        update_first_deposit_date(client_first_deposit_date.split('T')[0], params['id'])

    except KeyError:
        client_first_deposit_date = "Клиент не сделал первый депозит"

    client_id =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:Id']).replace("{'@i:nil': 'true'}", 'Нет данных')

    client_data = {
        "client_id": client_id,
        "client_first_deposit_date": client_first_deposit_date,
    }
    print(client_id, client_first_deposit_date.split('T')[0])
    return client_data


def get_clients_id_from_db(data_range):
    """ Получаем список client_id из базы данных.
     Getting a list of client_id from the database. """

    # Create a connection object
    connection = get_postgres_connection()

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    # Check if the database 'mm_bot' exists
    cursor.execute(f'''
                    SELECT client_id
                        FROM public.main_crmcheck
                        WHERE first_deposit_date IS NULL
                        AND call_result NOT IN ('есть фото', 'чужой номер', 'нет ответа') 
                        AND upload_date > '{data_range}'
                        ORDER BY client_id DESC;
                    ''')

    # Fetch all rows from the result set
    data = cursor.fetchall()

    # Close the cursor and connection to so the server can allocate
    # bandwidth to other requests
    cursor.close()
    connection.close()

    clients_id = [list(i)[0] for i in data]
    return clients_id


def update_first_deposit_date(verified_date, client_id):
    """ Обновляем дату верификации в базе данных.
     Updating the verification date in the database. """

    # Create a connection object
    connection = get_postgres_connection()

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    cursor.execute(f'''
                    UPDATE public.main_crmcheck
                        SET first_deposit_date = '{verified_date}',
                            first_deposit_amount = 1
                        WHERE client_id = {client_id};
                    ''')

    # Commit changes to the database
    connection.commit()

    # Close the cursor and connection to so the server can allocate
    # bandwidth to other requests
    cursor.close()
    connection.close()


def get_date_of_time_delta(delta):
    date_range = datetime.now() - timedelta(days=delta)
    return date_range

def main():
    """ Главная функция. Main function. """
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_range = get_date_of_time_delta(32).strftime('%Y-%m-%d')
    print(f"Start script at {current_date}")
    start_job_time = time.perf_counter()
    url = "https://backofficewebadmin.betconstruct.com/api/ru/Client/GetClientById?"

    clients_id = get_clients_id_from_db(date_range)
    # clients_id = [1406302873, ]

    count = 1
    count_all = len(clients_id)

    # Получаем данные для каждого client_id
    for client_id in clients_id:
        try:
            print(f"{count}/{count_all} Get data for client_id: {client_id}")
            params = set_params(client_id)
            get_data(url, params)
            count += 1
            time.sleep(6)
        except KeyError as e:
            print(f"{count}/{count_all} Get data for client_id: {client_id} KeyError: {e}")
            count += 1
            time.sleep(6)
            continue

    stop_job_time = time.perf_counter()
    working_time = stop_job_time - start_job_time

    print('Задание выполнено в:', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Затрачено времени:", str(timedelta(seconds=working_time)))



if __name__ == "__main__":
    main()
