# Открываем исходный файл для чтения
with open('111.txt', 'r', encoding='utf-8') as infile:
    # Читаем строки из исходного файла
    lines = infile.readlines()

# Создаем новый файл для записи
with open('222.txt', 'w', encoding='utf-8') as outfile:
    # Записываем заголовок
    outfile.write("Имя;Дата;Начальный баланс;Остаток средств;Сумма депозита\n")

    # Итерируемся по строкам из исходного файла
    for i in range(0, len(lines), 5):
        # Записываем пять строк в новый файл с разделителем ";"
        outfile.write(';'.join([line.strip() for line in lines[i:i + 5]]) + '\n')

print("Преобразование завершено. Результат записан в новый_файл.txt")
