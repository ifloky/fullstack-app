SELECT id, client_id, client_birthday, verified_date
	FROM public.main_clientsbirthday
	ORDER BY id DESC;
	
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


