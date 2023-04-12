import requests
import credentials
import time

from datetime import datetime, timedelta
from memory_profiler import memory_usage


def close_round_data_from_skks(skks_host, account_id, round_id, transaction_id, amount, actual_time):
    """ Эта функция получает данные из SKKS """
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'User-Agent': 'PostmanRuntime/7.29.2',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    body = {
        "_cmd_": "Transaction/Win",
        "actual_time": actual_time,
        "account_id": account_id,
        "round_id": round_id,
        "tr_id": transaction_id,
        "amount": amount,
        "tr_domain": 1,
        "currency_id": 1,

    }

    response = requests.post(
        url=skks_host,
        headers=headers,
        json=body,
    )
    print(response.text)
    status = response.json()['_status_']
    print(status)


def main():
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_job_time = time.perf_counter()
    print(f"Start script at {current_date}")

    skks_host = f'{credentials.skks_test_host}/Transaction/Win'

    # account_id = 1268338164  # Atrides
    account_id = 603031708  # ПУПКИНА ОЛЬГА АНДРЕЕВНА, BLR, КН2461094
    round_id = 119082783540  # Берем из раунда ставки
    transaction_id = 119082783760  # Берем из раунда выигрыша
    amount = 15
    actual_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")

    if amount == 0:
        transaction_id = round_id + 1  # Для нулевых раундов берем ID из раунда выигрыша и увеличиваем на единицу

    close_round_data_from_skks(skks_host, account_id, round_id, transaction_id, amount, actual_time)

    stop_job_time = time.perf_counter()
    working_time = stop_job_time - start_job_time

    print(f"Script finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Время выполнения:", str(timedelta(seconds=working_time)))
    print("Затрачено памяти:", (memory_usage())[-1], "Mb")


if __name__ == '__main__':
    main()
