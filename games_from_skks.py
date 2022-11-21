from datetime import time

import psycopg2
import requests
import credentials


def load_game_list_from_skks():
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
        f'{credentials.skks_host}/Game/ListPermitted',
        headers=headers,
        json=body,
    )
    return response.json()


def clear_data():
    connection = psycopg2.connect(database=credentials.db_name,
                                  user=credentials.db_username,
                                  password=credentials.db_password,
                                  host=credentials.db_host,
                                  port=credentials.db_port,
                                  )
    cursor = connection.cursor()
    cursor.execute(
        f"TRUNCATE TABLE main_gamelistfromskks RESTART IDENTITY CASCADE;")
    print(cursor.statusmessage)
    connection.commit()
    connection.close()


def save_game_list_to_db(game_list):
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
            f"INSERT INTO main_gamelistfromskks (game_id, game_type, game_name, game_permitted_date, game_provider) "
            f"VALUES ({game_id}, '{game_type}', '{game_name}', '{permitted_date}', '{vendor}')")
        counter += 1
        connection.commit()
        connection.close()
    print(f"Save total games: {counter}")


def main():
    game_list = load_game_list_from_skks()
    # pprint(game_list)
    clear_data()
    save_game_list_to_db(game_list)


if __name__ == '__main__':
    main()
