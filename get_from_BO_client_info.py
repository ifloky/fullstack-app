import csv
import time
import xmltodict
import requests

from datetime import timedelta, datetime
from temp import check_id
from credentials import backoffice_authentication, backoffice_cookie


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

    # Преобразуем XML в словарь
    response_dict = xmltodict.parse(response_str)

    parsed_data = response_dict

    address =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:Address']).replace("{'@i:nil': 'true'}", 'Нет данных')
    try:
        client_create_date =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:Created']['d3p1:DateTime']).replace("{'@i:nil': 'true'}", 'Нет данных')
    except KeyError:
        client_create_date = "Нет данных"

    try:
        client_verification_date =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:ClientVerificationDate']['d3p1:DateTime']).replace("{'@i:nil': 'true'}", 'Нет данных')
    except KeyError:
        client_verification_date = "Клиент не верифицирован"

    first_name = str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:FirstName']).replace("{'@i:nil': 'true'}", 'Нет данных')
    middle_name =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:MiddleName']).replace("{'@i:nil': 'true'}", 'Нет данных')
    last_name =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:LastName']).replace("{'@i:nil': 'true'}", 'Нет данных')

    birth_city =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:BirthCity']).replace("{'@i:nil': 'true'}", 'Нет данных')
    birth_department =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:BirthDepartment']).replace("{'@i:nil': 'true'}", 'Нет данных')
    birth_date =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:BirthDate']).replace("{'@i:nil': 'true'}", 'Нет данных')

    doc_issue_date =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:DocIssueDate']).replace("{'@i:nil': 'true'}", 'Нет данных')
    doc_issued_by =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:DocIssuedBy']).replace("{'@i:nil': 'true'}", 'Нет данных')
    doc_number =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:DocNumber']).replace("{'@i:nil': 'true'}", 'Нет данных')
    personal_id =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:PersonalId']).replace("{'@i:nil': 'true'}", 'Нет данных')

    balance =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:Balance']).replace("{'@i:nil': 'true'}", 'Нет данных')
    email =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:Email']).replace("{'@i:nil': 'true'}", 'Нет данных')
    phone =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:Phone']).replace("{'@i:nil': 'true'}", 'Нет данных')
    client_id =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:Id']).replace("{'@i:nil': 'true'}", 'Нет данных')
    last_ip =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:LastLoginIp']).replace("{'@i:nil': 'true'}", 'Нет данных')

    try:
        last_login_time =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:LastLoginTime']['d3p1:DateTime']).replace("{'@i:nil': 'true'}", 'Нет данных')
    except KeyError:
        last_login_time = "Клиент не авторизовался"

    is_locked =  str(parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:IsLocked']).replace("{'@i:nil': 'true'}", 'Нет данных')

    client_data = {
        "client_id": client_id,
        "last_name": last_name,
        "first_name": first_name,
        "middle_name": middle_name,
        "address": address,
        "birth_city": birth_city,
        "birth_department": birth_department,
        "birth_date": birth_date,
        "doc_issue_date": doc_issue_date,
        "doc_issued_by": doc_issued_by,
        "doc_number": doc_number,
        "personal_id": personal_id,
        "client_create_date": client_create_date,
        "client_verification_date": client_verification_date,
        "is_locked": is_locked,
        "phone": phone,
        "email": email,
        "last_ip": last_ip,
        "last_login_time": last_login_time,
        "balance": balance,
    }

    return client_data


def main():
    """ Главная функция. Main function. """
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Start script at {current_date}")
    start_job_time = time.perf_counter()
    url = "https://backofficewebadmin.betconstruct.com/api/ru/Client/GetClientById?"

    clients_data = []

    count = 1
    count_all = len(check_id)

    # clients_id = check_id
    clients_id = [309923352,291298827,277689892,310196004]

    # Получаем данные для каждого client_id
    for client_id in clients_id:
        try:
            print(f"{count}/{count_all} Get data for client_id: {client_id}")
            params = set_params(client_id)
            client_info = get_data(url, params)
            clients_data.append(client_info)
            count += 1
            time.sleep(6)
        except KeyError as e:
            print(f"{count}/{count_all} Get data for client_id: {client_id} KeyError: {e}")
            count += 1
            time.sleep(6)
            continue



    # Записываем данные в CSV файл
    # Write data to CSV file
    with open('clients_data.csv', 'w', newline='', encoding='UTF-8') as csvfile:
        fieldnames = ['client_id', 'last_name', 'first_name', 'middle_name', 'address', 'birth_city',
                      'birth_department', 'birth_date', 'doc_issue_date', 'doc_issued_by', 'doc_number',
                      'personal_id', 'client_create_date', 'client_verification_date', 'is_locked', 'phone',
                      'email', 'last_ip', 'last_login_time', 'balance']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for client in clients_data:
            writer.writerow(client)

    stop_job_time = time.perf_counter()
    working_time = stop_job_time - start_job_time

    print('Задание выполнено в:', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(f"Get data for {len(clients_data)} clients")
    print("Затрачено времени:", str(timedelta(seconds=working_time)))



if __name__ == "__main__":
    main()
