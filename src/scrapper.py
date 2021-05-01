import os
import time
import json
import requests
import csv
from bs4 import BeautifulSoup

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def main():
    cls()
    baseURL     = "https://www.imdb.com/title/tt"
    startURL    = 0
    endURL      = 9999999




    table = []
    for i in range(startURL, endURL):
        titleFixed = str(i).zfill(7)
        url = baseURL + titleFixed + '/'
        row = []
        try:
            html = requests.get(url).text
            soup = BeautifulSoup(html, 'html.parser')
            data = json.loads(soup.find('script', type='application/ld+json').string)

            if(data['@type'] == 'Movie'):
                f = open("/opt/storage/movies.csv", "a")
            if(data['@type'] == 'TVSeries'):
                f = open("/opt/storage/series.csv", "a")

            write = csv.writer(f)
            row.append(data['name'])
            row.append(url)
            row.append(data['genre'])
            row.append(data['aggregateRating']['ratingValue'])
            try:
                row.append(data['datePublished'])
            except Exception as e:
                pass
            write.writerow(row)
            f.close()
            print(row)
        except Exception as e:
            print(e)
            '''
            # TODO:
            If Error, output to log file
            '''


if __name__ == "__main__":
    main()
