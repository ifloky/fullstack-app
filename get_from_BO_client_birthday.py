import time
import xmltodict
import requests
import psycopg2

from datetime import timedelta, datetime
from credentials import backoffice_authentication, backoffice_cookie
from credentials import db_name, db_username, db_password, db_host, db_port
from credentials import fd_db_username, fd_db_password, fd_db_host, fd_db_port, fd_db_name


def get_postgres_connection():
    """ This function creates a connection to Postgres DB """
    try:
        connection = psycopg2.connect(user=db_username,
                                      password=db_password,
                                      host=db_host,
                                      port=db_port,
                                      database=db_name)
        return connection
    except Exception as e:
        print(e)


def get_fd_postgres_connection():
    """ This function creates a connection to Postgres DB """
    try:
        connection = psycopg2.connect(user=fd_db_username,
                                      password=fd_db_password,
                                      host=fd_db_host,
                                      port=fd_db_port,
                                      database=fd_db_name)
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
        client_verification_date = str(
            parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:ClientVerificationDate'][
                'd3p1:DateTime']).replace("{'@i:nil': 'true'}", 'Нет данных')
        client_birthday = str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:BirthDate']).replace(
            "{'@i:nil': 'true'}", 'Нет данных')

        print('', 'Записываем дата рождения клиента:',params['id'], client_birthday.split('T')[0])
        save_birth_date(params['id'], client_birthday.split('T')[0], client_verification_date.split('T')[0])

    except KeyError:
        client_birthday = "Клиент не верифицирован"
        print('', client_birthday)

    client_id =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:Id']).replace("{'@i:nil': 'true'}", 'Нет данных')

    client_data = {
        "client_id": client_id,
        "client_birthday": client_birthday,
    }
    return client_data


def get_clients_id_from_bo_db():
    """ Получаем список client_id из базы данных.
     Getting a list of client_id from the database. """

    # Create a connection object
    connection = get_fd_postgres_connection()

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    # Check if the database 'mm_bot' exists
    cursor.execute(f'''
                    SELECT client_id, verification_date
                    FROM public.v_client_deposit
                    WHERE verification_date IS NOT NULL
                    ORDER BY verification_date DESC
                    ''')

    # Fetch all rows from the first result set
    data = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()

    # Create a connection object for the second query
    connection2 = get_postgres_connection()

    # Create a cursor object for the second query
    cursor2 = connection2.cursor()

    # Execute the second query to get client_id from 'main_clientsbirthday'
    cursor2.execute('''
                    SELECT client_id
                    FROM public.main_clientsbirthday
                    ORDER BY client_id DESC
                    ''')

    # Fetch all rows from the second result set
    data2 = cursor2.fetchall()

    # Close the cursor and connection for the second query
    cursor2.close()
    connection2.close()

    # Extract client_id values from both result sets
    clients_id1 = [row[0] for row in data]
    clients_id2 = [row[0] for row in data2]

    # Filter out client_id values from the first result set that are not in the second result set
    filtered_clients_id = [client_id for client_id in clients_id1 if client_id not in clients_id2]

    return filtered_clients_id


def save_birth_date(client_id, birth_date, verification_date):
    """ Сохраняем бару рождения и верификации в базе данных. """

    # Create a connection object
    connection = get_postgres_connection()

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    # Save data to the database
    cursor.execute(f'''
                    INSERT INTO public.main_clientsbirthday
                        (client_id, client_birthday, verified_date)
                        VALUES ({client_id}, '{birth_date}', '{verification_date}')
                    ''')

    # Commit the changes to the database
    connection.commit()

    # Close the cursor and connection to so the server can allocate
    # bandwidth to other requests
    cursor.close()
    connection.close()

    # print(f"Data for client_id: {client_id} saved to the database.")


def get_date_of_time_delta(delta):
    date_range = datetime.now() - timedelta(days=delta)
    return date_range

def main():
    """ Главная функция. Main function. """
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Start script at {current_date}")
    start_job_time = time.perf_counter()
    url = "https://backofficewebadmin.betconstruct.com/api/ru/Client/GetClientById?"

    clients_id = get_clients_id_from_bo_db()
    # clients_id = [1406302873, ]

    count = 1
    count_all = len(clients_id)

    # Получаем данные для каждого client_id
    for client_id in clients_id:
        try:
            print(f"{count}/{count_all} Get data for client_id: {client_id}", end='')
            params = set_params(client_id)
            get_data(url, params)
            count += 1
            time.sleep(6)
        except KeyError as e:
            print(f"{count}/{count_all} Get data for client_id: {client_id} KeyError: {e}", end='')
            count += 1
            time.sleep(6)
            continue

    stop_job_time = time.perf_counter()
    working_time = stop_job_time - start_job_time

    print('Задание выполнено в:', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Затрачено времени:", str(timedelta(seconds=working_time)))



if __name__ == "__main__":
    main()
