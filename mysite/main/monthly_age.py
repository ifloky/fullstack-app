from credentials import db_host, db_port, db_name, db_username, db_password
from datetime import timedelta, datetime

import psycopg2

import pandas as pd

def get_sql_connection():
    print('Connecting to PostgreSQL database...')
    try:
        connection = psycopg2.connect(host=db_host,
                                      port=db_port,
                                      database=db_name,
                                      user=db_username,
                                      password=db_password)
        return connection
    except Exception as e:
        print(e)



def create_df_count():
    print('Creating Count DataFrame...')
    df = []
    try:
        connection = get_sql_connection()
        cursor = connection.cursor()
        query = (F'''
                SELECT
                    TO_CHAR(DATE_TRUNC('month', verified_date), 'YYYY-MM') AS month,
                    COUNT(CASE WHEN age BETWEEN 21 AND 24 THEN 1 ELSE NULL END) AS "21-24",
                    COUNT(CASE WHEN age BETWEEN 25 AND 34 THEN 1 ELSE NULL END) AS "25-34",
                    COUNT(CASE WHEN age BETWEEN 35 AND 44 THEN 1 ELSE NULL END) AS "35-44",
                    COUNT(CASE WHEN age BETWEEN 45 AND 54 THEN 1 ELSE NULL END) AS "45-54",
                    COUNT(CASE WHEN age BETWEEN 55 AND 64 THEN 1 ELSE NULL END) AS "55-64",
                    COUNT(CASE WHEN age > 65 THEN 1 ELSE NULL END) AS "более 65",
                    COUNT(*) AS "Общее количество"
                FROM (
                    SELECT
                        client_id,
                        DATE_PART('year', verified_date) - DATE_PART('year', client_birthday) - CASE WHEN DATE_TRUNC('year', verified_date) < client_birthday THEN 1 ELSE 0 END AS age,
                        verified_date
                    FROM
                        public.main_clientsbirthday
                ) AS subquery
                GROUP BY
                    TO_CHAR(DATE_TRUNC('month', verified_date), 'YYYY-MM')
                ORDER BY
                    TO_CHAR(DATE_TRUNC('month', verified_date), 'YYYY-MM');
                ''')
        cursor.execute(query)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=[c[0] for c in cursor.description])
        cursor.close()
        connection.close()
    except Exception as e:
        print(e)
    # print(df)
    return df


def create_df_percent():
    print('Creating Count DataFrame...')
    df = []
    try:
        connection = get_sql_connection()
        cursor = connection.cursor()
        query = (F'''
                WITH MonthlyCounts AS (
                    SELECT
                        TO_CHAR(DATE_TRUNC('month', verified_date), 'YYYY-MM') AS month,
                        COUNT(*) AS total_count,
                        COUNT(CASE WHEN age BETWEEN 21 AND 24 THEN 1 ELSE NULL END) AS "21-24",
                        COUNT(CASE WHEN age BETWEEN 25 AND 34 THEN 1 ELSE NULL END) AS "25-34",
                        COUNT(CASE WHEN age BETWEEN 35 AND 44 THEN 1 ELSE NULL END) AS "35-44",
                        COUNT(CASE WHEN age BETWEEN 45 AND 54 THEN 1 ELSE NULL END) AS "45-54",
                        COUNT(CASE WHEN age BETWEEN 55 AND 64 THEN 1 ELSE NULL END) AS "55-64",
                        COUNT(CASE WHEN age > 65 THEN 1 ELSE NULL END) AS "более 65"
                    FROM (
                        SELECT
                            client_id,
                            DATE_PART('year', verified_date) - DATE_PART('year', client_birthday) - CASE WHEN DATE_TRUNC('year', verified_date) < client_birthday THEN 1 ELSE 0 END AS age,
                            verified_date
                        FROM
                            public.main_clientsbirthday
                    ) AS subquery
                    GROUP BY
                        TO_CHAR(DATE_TRUNC('month', verified_date), 'YYYY-MM')
                )
                SELECT
                    month,
                    ROUND(("21-24" / total_count::numeric * 100)::numeric) AS "21-24 (%)",
                    ROUND(("25-34" / total_count::numeric * 100)::numeric) AS "25-34 (%)",
                    ROUND(("35-44" / total_count::numeric * 100)::numeric) AS "35-44 (%)",
                    ROUND(("45-54" / total_count::numeric * 100)::numeric) AS "45-54 (%)",
                    ROUND(("55-64" / total_count::numeric * 100)::numeric) AS "55-64 (%)",
                    ROUND(("более 65" / total_count::numeric * 100)::numeric) AS "более 65 (%)"
                FROM MonthlyCounts
                ORDER BY month;
                ''')

        cursor.execute(query)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=[c[0] for c in cursor.description])
        cursor.close()
        connection.close()
    except Exception as e:
        print(e)
    # print(df)
    return df


def main():
    df_count = create_df_count()
    df_percent = create_df_percent()
    print(df_count)
    print(df_percent)


if __name__ == "__main__":
    main()