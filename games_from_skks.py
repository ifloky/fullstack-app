import psycopg2
import requests
import credentials
import datetime


def load_game_list_from_skks(host_name):
    """
    Get game lest from skks system.
    """
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'User-Agent': 'PostmanRuntime/7.29.2',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    body = {
        "_cmd_": "Game/ListPermitted"
    }

    response = requests.post(
        f'{host_name}/Game/ListPermitted',
        headers=headers,
        json=body,
    )
    return response.json()


def clear_data(db_name):
    connection = psycopg2.connect(database=credentials.db_name,
                                  user=credentials.db_username,
                                  password=credentials.db_password,
                                  host=credentials.db_host,
                                  port=credentials.db_port,
                                  )
    cursor = connection.cursor()
    cursor.execute(
        f"TRUNCATE TABLE {db_name} RESTART IDENTITY CASCADE;")
    print(cursor.statusmessage)
    connection.commit()
    connection.close()


def save_game_list_to_db(game_list, db_name):
    """ Save game list to db. """
    counter = 0
    for x in game_list['games']:
        game_id: str = x['game_id']
        game_type: str = x['game_type']
        game_name: str = x['name'].replace("'", "''")
        try:
            vendor: str = x['vendor_name']
        except KeyError:
            vendor = str('BetConstruct')
        permitted_date: str = x['permitted_at']

        connection = psycopg2.connect(database=credentials.db_name,
                                      user=credentials.db_username,
                                      password=credentials.db_password,
                                      host=credentials.db_host,
                                      port=credentials.db_port,
                                      )
        cursor = connection.cursor()
        cursor.execute(
            f"INSERT INTO {db_name} (game_id, game_type, game_name, game_permitted_date, game_provider) "
            f"VALUES ({game_id}, '{game_type}', '{game_name}', '{permitted_date}', '{vendor}')")
        counter += 1
        connection.commit()
        connection.close()
    print(f"Save total games: {counter}")


def main():
    """ Main function. """
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Start script at {current_date}")
    prod_host = credentials.skks_host
    test_host = credentials.skks_test_host
    game_prod_list = load_game_list_from_skks(prod_host)
    db_prod_name = 'main_gamelistfromskks'
    game_test_list = load_game_list_from_skks(test_host)
    db_test_name = 'main_gamelistfromskkstest'
    clear_data(db_prod_name)
    save_game_list_to_db(game_prod_list, db_prod_name)

    clear_data(db_test_name)
    save_game_list_to_db(game_test_list, db_test_name)


if __name__ == '__main__':
    main()
