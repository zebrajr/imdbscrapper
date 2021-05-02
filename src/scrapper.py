import os
import time
import json
import requests
import csv
import logging
from bs4 import BeautifulSoup

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def main():
    cls()
    baseURL     = "https://www.imdb.com/title/tt"       # Base URL for each title
    startURL    = 0                                     # Start Number
    endURL      = 9999999                               # Ending Number
    debugLevel  = 40                                    # 20 will display Info messages, 40 errors
    logFile     = "/opt/storage/info.log"               # Log output
    counterFile = "/opt/storage/counter.txt"            # Which ID was last scanned


    table = []
    try:
        counter = open(counterFile, "r")
        startURL = int(counter.read())
        counter.close()
    except Exception as e:
        pass
    for i in range(startURL, endURL):
        logging.basicConfig(filename=logFile, level=logging.INFO)
        titleFixed = str(i).zfill(7)        # Adds leading zeros, so that it always has 7 digits
        url = baseURL + titleFixed + '/'    # String Joins every part of the URL
        row = []                            # Clears the row list
        try:
            # Requests, parses and loads into JSON the HTML response
            html = requests.get(url).text
            soup = BeautifulSoup(html, 'html.parser')
            data = json.loads(soup.find('script', type='application/ld+json').string)

            # Sorting into Movies and Shows, based on a file
            if(data['@type'] == 'Movie'):
                f = open("/opt/storage/movies.csv", "a")
            if(data['@type'] == 'TVSeries'):
                f = open("/opt/storage/series.csv", "a")

            # Gets the desired values from the JSON response
            row.append(data['name'])
            try:
                row.append(data['description'])
            except Exception as e:
                row.append("Description unavailable")
            row.append(url)
            try:
                row.append(data['genre'])
            except Exception as e:
                row.append("Genre Unknown")
            try:
                row.append(data['aggregateRating']['ratingValue'])
            except Exception as e:
                row.append("No Rating")
            try:
                row.append(data['aggregateRating']['ratingCount'])
            except Exception as e:
                row.append("Total Rating Count N/A")
            try:
                row.append(data['datePublished'])
            except Exception as e:
                row.append("Unknown")
            # Opens, writes and closes the file with the information of the movie / series
            write = csv.writer(f)
            write.writerow(row)
            if(debugLevel <= 20):
                logging.info(row)
            f.close()

            counter = open(counterFile, "w")
            counter.write(str(i))
            counter.close()

            print(row)      # Prints to the screen, in case the user is watching the Docker / software in foreground
        except Exception as e:
            # Writes to the log if an error is found
            errorMessage = titleFixed + " - " + str(e)
            logging.error(errorMessage)



if __name__ == "__main__":
    main()
