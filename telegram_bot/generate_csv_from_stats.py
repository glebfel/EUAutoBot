import csv
import pathlib

from databases import get_all_users_stats

# current directory
DIR_PATH = str(pathlib.Path(__file__).parent)


def create_csv():
    with open(DIR_PATH + '/stats.csv', mode='w') as csv_file:
        fieldnames = ['ID пользователя',
                      'Количество использований бота',
                      'Количество запросов на проведение расчета стоимости авто',
                      'Количество запросов на получение обратной связи (звонки)',
                      'Дата последнего использования']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        users_data = get_all_users_stats()
        for _ in users_data:
            writer.writerow(_)
