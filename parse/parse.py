import datetime
import requests
from bs4 import *
import os
import pandas as pd

URL_TEMPLATE = 'https://www.work.ua/jobs/?salaryfrom=2&salaryto=9&page='


def calcResult(value: str):
    a, b = map(int, value.split('-'))
    return str(int((a + b)/2))


def getMonth(month: str):
    Array = {'сі': '01', 'лю': '02', 'бе': '03', 'кв': '04', 'тр': '05', 'че': '06', 'ли': '07', 'се': '08', 'ве': '09', 'жо': '10','ли': '11', 'гр': '12'}
    try:
        return Array[month]
    except:
        return 'NaN'


def getJobCards(page: BeautifulSoup):
    cards = page.find_all('div', class_ = 'card-hover')
    return cards


def getInfoFromCard(card: BeautifulSoup):
    url = card.find('a')
    request = requests.get('https://www.work.ua'+url['href'])
    page = BeautifulSoup(request.text, 'html.parser')
    name = page.find('h1', id = 'h1-name').text
    salary = page.find('b', class_ = 'text-black').text.replace('\u202f', '').replace(' грн', '')
    if salary.find("–") != -1:
        salary = salary.replace('\u2009–\u2009', '-')
        salary = calcResult(salary)
    town = ' '.join(page.find('p', class_ = 'text-indent add-top-sm').text.split())
    if town.find(",") != -1:
        town = town[ : town.find(",")]
    description = ' '.join(page.find('div', id = 'job-description').text.replace('\n', ' ').split())
    try:
        company = page.find_all('b')[1].text
    except:
        company = 'NaN'
    date = page.find('p', class_ = 'cut-bottom-print').text.replace('\n', '')
    if date[-15:] == 'Гаряча вакансія':
        date = datetime.datetime.today().strftime("%d-%m-%Y")
    else:
        day, month, year = list(map(str, date.split(" ")))[-3:]
        day = list(map(str, day.split("\xa0")))[1]
        month = getMonth(month[:2])
        date = day + '-' + month + '-' + year
    return {'name': name, 'url': 'https://www.work.ua'+url['href'], 'company': company, 'salary': salary, 'town': town, 'date': date, 'description': description}


def getThreshold(page: BeautifulSoup):
    return int(page.find('ul', class_ = 'pagination hidden-xs').find_all('a')[-2].text)


if __name__ == "__main__":
    Result = {'name': [], 'url': [], 'company': [], 'salary': [], 'town': [], 'date': [], 'description': []}
    request = requests.get(URL_TEMPLATE+'1')
    page = BeautifulSoup(request.text, 'html.parser')
    start = 1
    threshold = getThreshold(page)
    exceptValue = 0
    print('Начинаю работу, делаю запрос к домену - www.work.ua\nСтраниц обнаружено', threshold)
    for i in range(start, threshold + 1):
        try:
            request = requests.get(URL_TEMPLATE+str(i))
            page = BeautifulSoup(request.text, 'html.parser')
            for card in getJobCards(page):
                Array = getInfoFromCard(card)
                Result['name'].append(Array['name'])
                Result['company'].append(Array['company'])
                Result['salary'].append(Array['salary'])
                Result['town'].append(Array['town'])
                Result['date'].append(Array['date'])
                Result['url'].append(Array['url'])
                Result['description'].append(Array['description'])
            os.system('cls')
            print(round(i/threshold*100, 2),'% обработал, статус -> OK, ошибок =', exceptValue)
        except:
            os.system('cls')
            exceptValue += 1
            print(round(i/threshold*100, 2),'% обработал, статус -> BAD, ошибок =', exceptValue)
    if exceptValue == 0:
        print('Оконченно. статус -> OK, обработано страниц', threshold, '.')
    else:
        print('Оконченно. статус -> BAD, ошибок =', exceptValue, 'из', threshold, 'страниц.')
    print('Скачалось вакансий -', len(Result['name']))
    df = pd.DataFrame(Result)
    date = datetime.datetime.today().strftime("%d-%m-%Y")
    path = 'df_' + date + '.csv'
    df.to_csv(path)
    print('Данные сохранены в', path)
    input('Введите что угодно для выхода...\n')
