import os
import time
import json
import requests
import csv
import logging
from threading import Thread
from bs4 import BeautifulSoup

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def imdbscrapper(i):
    cpuCount        = int(os.cpu_count()) - 1
    baseURL         = "https://www.imdb.com/title/tt"       # Base URL for each title
    startURL        = 9999999                               # Start Number
    endURL          = 0                                     # Ending Number
    debugLevel      = 40                                    # 20 will display Info messages, 40 errors
    logFile         = "/opt/storage/info.log"               # Log output
    counterFileBase = "/opt/storage/counter"            # Base for the counter file
    counterFileExt  = ".txt"
    #counterFile     = "/opt/storage/counter.txt"            # Which ID was last scanned
    reCheckFile     = "/opt/storage/recheck.txt"            # Which IDs to recheck


    startURL = int((startURL/cpuCount)*i)
    endURL = int(i*(startURL/cpuCount)+1)


    try:
        # Tries to read the value to continue from counterN.txt. On error defaults to StartURL
        counterFile = counterFileBase + str(i) + counterFileExt
        counter = open(counterFile, "r")
        startURL = int(counter.read())
        counter.close()
    except Exception as e:
        pass
    for i in range(startURL, endURL, -1):
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

            print(row)      # Prints to the screen, in case the user is watching the Docker / software in foreground
        except Exception as e:
            # Writes to the log if an error is found
            errorMessage = titleFixed + " - " + str(e)
            logging.error(errorMessage)
            # If the error is page not available, add to file (Perforance improvement on rechecks)
            if("NoneType" in str(e)):
                recheck = open(reCheckFile, "a")
                recheckString = titleFixed + "\n"
                recheck.write(recheckString)
                recheck.close()
        finally:
            # Updates the Counter on file
            counter = open(counterFile, "w")
            counter.write(str(i))
            counter.close()

def main():
    cls()
    # Comment in/out if you want 90% or full performance (not implemented)
    cpuCount        = int(os.cpu_count()) - 1
    #cpuCount        = 4

    threads = []
    for i in range(cpuCount):
        print(i)
        threads.append(Thread(target=imdbscrapper(i)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
