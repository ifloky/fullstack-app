import csv
import datetime
import xmltodict
import requests

from time import sleep


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
        "Authentication": "c9b237cde4552ab509bad0d2687fa6ae22615139c8094c1f49db93c54b44fec6",

        "Cookie":
        "SERVERID=172.16.202.166; "
        "_ym_uid=1668417668495845880; "
        "_ym_d=1668417668; "
        "_hjSessionUser_2896749=eyJpZCI6IjhkMTEzMGJlLWRlODYtNTI5Ni1iZDJiLTc0ZTkyNTczNTFkYiIsImNyZWF0ZWQiOjE2Njg0MTc2NjkzNTksImV4aXN0aW5nIjpmYWxzZX0=; "
        "ajs_anonymous_id=d6494813-4d1a-4ddf-b25a-26718d5459dc; "
        "intercom-id-xocfnqo5=848a34aa-01ca-46a7-986c-007dbe18372b; "
        "_ga=GA1.1.1578264362.1667472391; "
        "_ga_XG5GYYCNNL=GS1.1.1683791605.2.1.1683791621.0.0.0; "
        "bo_logout_token=eyJhbGciOiJSUzI1NiIsImtpZCI6IjU3ZGRhMzlhNjhjOWE1NWZiYWRjMmUwODJhMTVjZTlmIiwidHlwIjoiSldUIn0.eyJuYmYiOjE2ODQxMzU5MjMsImV4cCI6MTY4NDEzNjIyMywiaXNzIjoiaHR0cHM6Ly9hcGkuYWNjb3VudHMtYmMuY29tIiwiYXVkIjoiQmFja09mZmljZVNTTyIsIm5vbmNlIjoiaHR0cHM6Ly9iYWNrb2ZmaWNld2ViYWRtaW4uYmV0Y29uc3RydWN0LmNvbSIsImlhdCI6MTY4NDEzNTkyMywiYXRfaGFzaCI6IkRkU2d6N0lrd2l3SXdTUThLNnlEbmciLCJjX2hhc2giOiJJTHliREpPOWJURjY1cUZQVWozaTZBIiwic2lkIjoiZGQ2NWJhMWVlOGQ5MWQzYmUxYTNlNDY3NmQxZWFkYjAiLCJzdWIiOiI2MjQwYWY2Ni1jZDZhLTRjOTEtOWQzZS00NDg4ODdiYWFmNjkiLCJhdXRoX3RpbWUiOjE2ODQxMzU5MjIsImlkcCI6ImxvY2FsIiwiYW1yIjpbInB3ZCJdfQ.X1K44nR3X3_nXFcavkkh073DTHXW9qeIOtqEQ9InOnNnr9km-18NUexqR5ylWmLUYeiroRjtH75EnuFKKrSQhE9AQyZPWiqdrDNNQgHWQcZBDF3-m--6OV06mLRJ2qFD96sWvK1ABX2tEUKUoJKt9KL4vZkKX8_qgE67qGL0Wbec0xpOsofra-9S2H4v1bA3V42yfgfld22TlVpDXLiLXxt9o1jjL3HQ0S8gcskbgk5mhjDQtnWPMmIq2y3a_9yQ7GwDUuWXzO8xghhl3LBcY257yYCP4Fd-4sOWDX8UONhi797h6NQjV98t_lGD5Nk_T3KiXRt_4Zh1yGSG9KAzTw; "
        "sid=dd65ba1ee8d91d3be1a3e4676d1eadb0",

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

    # Преобразуем XML в словарь
    response_dict = xmltodict.parse(response_str)

    parsed_data = response_dict

    address = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:Address']

    client_create_date = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:Created']['d3p1:DateTime']
    client_verification_date = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:ClientVerificationDate'][
        'd3p1:DateTime']

    first_name = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:FirstName']
    middle_name = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:MiddleName']
    last_name = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:LastName']

    birth_city = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:BirthCity']
    birth_department = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:BirthDepartment']
    birth_date = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:BirthDate']

    doc_issue_date = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:DocIssueDate']
    doc_issued_by = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:DocIssuedBy']
    doc_number = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:DocNumber']
    personal_id = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:PersonalId']

    balance = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:Balance']
    email = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:Email']
    phone = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:Phone']
    client_id = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:Id']
    last_ip = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:LastLoginIp']
    last_login_time = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:LastLoginTime']['d3p1:DateTime']
    is_locked = parsed_data['ResponseModelOfClientModelNm0NiJ3A']['Data']['d2p1:IsLocked']

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
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Start script at {current_date}")
    url = "https://backofficewebadmin.betconstruct.com/api/ru/Client/GetClientById?"

    clients_data = []

    clients_id = [1019122912, 375219441,]
    for client_id in clients_id:
        print(f"Get data for client_id: {client_id}")
        params = set_params(client_id)
        client_info = get_data(url, params)
        clients_data.append(client_info)
        sleep(5)

    print(f"Get data for {len(clients_data)} clients")

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


if __name__ == "__main__":
    main()
