import datetime
import re
from pprint import pprint

import requests
import psycopg2
import credentials


def set_headers():
    """ Задаем параметры заголовков для веб запросов.
     Setting header parameters for web requests. """

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3;q=0.9",
        "cookie": "_ym_uid=1664358174761921314; _ym_d=1664358174; _gcl_au=1.1.2051354054.1664358174; "
                  "tmr_lvid=e3d91264d22eeb61916a2c8491fe0b32; tmr_lvidTS=1664358174755; "
                  "_ga=GA1.2.1624125713.1664358175; _fbp=fb.1.1664358175304.391659808; "
                  "_immortal|user-hash=mevSGXtVQj-89BlYZjI82dYOJbTsZJX8C_en; lastlanguage=ru; "
                  "_gid=GA1.2.1314697763.1669025324; _ym_isad=2; country=BY; _ym_visorc=w; "
                  "tmr_detect=0|1669034955762; tmr_reqNum=369",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/107.0.0.0 Safari/537.36 "
    }

    return headers


def set_params():
    """ Задаем параметры для запроса.
     Setting parameters for the request. """

    params = {
        'partner_id': '1333',
        'is_mobile': '0',
        'lang': 'rus',
        'use_webp': '1',
        'offset': '0',
        'limit': '1',
        'category': '240, 60, 284, 125, 301, 57, 414, 246, 62, 95, 247, 51, 94, 40, 93, 28',
    }

    return params


def get_games_count(url, params):
    """ Получаем количество игр.
     Getting the number of games. """

    html = get_data(url, params)
    games_count = html.json()['total_count']

    return games_count


def get_data(url, params):
    """ Получаем html код страницы.
     Getting html code of the page. """

    r = requests.get(url, headers=set_headers(), params=params)
    return r


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


def get_game_info(game_date, db_name):
    """ Получаем информацию о играх.
     Getting information about games. """

    counter = 0
    game_data = game_date.json()['games']

    pprint(game_data)

    for game in game_data:
        game_name = game['name'].replace("'", "''").replace('™', '')
        game_name_find = re.sub(r"[^a-zA-Zа-яА-Я0-9]+", "", game['name'].lower())
        game_provider = game['provider_title']
        game_status = game['status']
        game_rtp = game['rtp']

        connection = psycopg2.connect(database=credentials.db_name,
                                      user=credentials.db_username,
                                      password=credentials.db_password,
                                      host=credentials.db_host,
                                      port=credentials.db_port,
                                      )
        cursor = connection.cursor()
        cursor.execute(
            f"INSERT INTO {db_name} (game_name, game_provider, game_status, game_name_find, game_rtp) "
            f"VALUES ('{game_name}', '{game_provider}', '{game_status}', '{game_name_find}', '{game_rtp}');")
        counter += 1
        connection.commit()
        connection.close()

        # print(f"{counter}, Game name: {game_name}, "
        #       f"Game provider: {game_provider}, "
        #       f"Game status: {game_status}"
        #       f"Game RTP: {game_rtp}")

    print(f"Save total games: {counter}")


def main():
    """ Главная функция.
     Main function. """
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Start script at {current_date}")
    url = "https://cmsbetconstruct.com/casino/getGames?"
    params = set_params()

    games_count = get_games_count(url, params)
    games_count = games_count
    print('Всего игр на сайте:', games_count)
    params['limit'] = games_count
    game_data = get_data(url, params)

    db_name = 'main_gamelistfromsite'
    clear_data(db_name)
    get_game_info(game_data, db_name)


if __name__ == "__main__":
    main()
