import pandas as pd

# Загрузка данных из первой таблицы
df1 = pd.read_excel('123456.xlsx', sheet_name='Лист1')

# Загрузка данных из второй таблицы
df2 = pd.read_excel('123456.xlsx', sheet_name='Лист2')

# Сравнение таблиц и вывод различий
diff = pd.concat([df1, df2]).drop_duplicates(keep=False)
print(diff)