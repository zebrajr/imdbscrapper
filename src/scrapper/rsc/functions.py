import mysql.connector as mariadb
from time import sleep


# Creates and returns a mariadb connection object
def createDBConnection():
    mydb = mariadb.connect(
        host = 'imdbdb',
        user = 'root',
        password = 'secret',
        database = 'imdbscrapper'
    )
    return mydb

'''
    Function to save data from lists (eg: movieTable) to file (eg: moviesFile)
'''
def saveToFile(dataTable, dataPath):
    # Assume we couldn't open / write to file
    sucessTest = False
    while sucessTest != True:
        # Try to open the file and append to it
        # [ToDo:] change try position to fix duplicate entries
        try:
            f = open(dataPath, "a")
            for row in dataTable:
                # Initialize an empty Output String
                outputStr = ""
                # For each value in the list, add it as string to the output, separate each by ";"
                for index, value in enumerate(row):
                    outputStr += str(value) + ";"
                # Adds the new line (\n) to the string, writes to the file, prints to the screen
                outputStr += "\n"
                f.write(outputStr)
                print(row)
            f.close()
            # If sucess, then file can move on
            sucessTest = True
        except Exception as e:
            print("Retrying updating - %s - %s" % (dataPath, e))

'''
    Function to check for duplicate entries in the database
    If found will return False
'''
def checkForDuplicate(idCheck):
    tablesToCheck = ['checkDuplicateMovie', 'checkDuplicateSerie', 'checkDuplicateIgnore', 'checkDuplicateRecheck']
    for table in tablesToCheck:
        mydb = createDBConnection()
        cursor = mydb.cursor(buffered=True)
        cursor.callproc(table, [idCheck,])
        for results in cursor.stored_results():
            result = results.fetchall()
        commitDBConnection(mydb)
        if len(result) > 0:
            return False

'''
    Remove Duplicates from the Main Tables
'''
def removeDuplicates():
    # Remove Duplicate Movies
    mydb = createDBConnection()
    cursor = mydb.cursor(buffered=True)
    cursor.callproc('getDuplicateMovies')
    for results in cursor.stored_results():
        result = results.fetchall()
    commitDBConnection(mydb)
    for row in result:
        mydb = createDBConnection()
        cursor = mydb.cursor(buffered=True)
        print("Removing duplicate:: %s" %(row[0]))
        cursor.callproc('removeDuplicateMovie', [row[0], row[1],])
        commitDBConnection(mydb)

    # Remove Duplicate Series
    # [TODO] D.R.Y
    mydb = createDBConnection()
    cursor = mydb.cursor(buffered=True)
    cursor.callproc('getDuplicateSeries')
    for results in cursor.stored_results():
        result = results.fetchall()
    commitDBConnection(mydb)
    for row in result:
        mydb = createDBConnection()
        cursor = mydb.cursor(buffered=True)
        print("Removing duplicate:: %s" %(row[0]))
        cursor.callproc('removeDuplicateSerie', [row[0], row[1],])
        commitDBConnection(mydb)



def commitDBConnection(database):
    database.commit()
    database.close()

def saveIgnoreToDatabase(idIgnore):
    mydb = createDBConnection()
    cursor = mydb.cursor(buffered=True)
    cursor.callproc('insertIgnore', [idIgnore,])
    commitDBConnection(mydb)

def saveRecheckToDatabase(idRecheck):
    mydb = createDBConnection()
    cursor = mydb.cursor(buffered=True)
    cursor.callproc('insertRecheck', [idRecheck,])
    commitDBConnection(mydb)


'''
    Function to save to the database
'''
def saveToDatabase(dataTable, inTable):
    # [TODO] Change to dynamic values from docker-compose.yml
    mydb = createDBConnection()
    cursor = mydb.cursor(buffered=True)

    # Defines which procedures to call
    if (inTable == 'movies'):
        mainTable = 'insertMovie'
        genreTable = 'insertMovieGenre'
    if (inTable == 'series'):
        mainTable = 'insertSerie'
        genreTable = 'insertSerieGenre'

    for row in dataTable:
        print("Found %s" %(row[0]))
        cursor.callproc(mainTable, [row[0],row[1],row[2],row[3],row[5],row[6],row[7],])
        try:
            if len(row[4]) > 1:
                for genre in row[4]:
                    cursor.callproc(genreTable, [row[0],genre,])
                continue
        except Exception as e:
            cursor.callproc(genreTable, [row[0],str(row[4]),])
    commitDBConnection(mydb)



'''
    Main Function for the scrapper
    It will prepare the URL, request it, get the answer, parse the information to a list,
        append that list to another list and finally call savetoFile(dataTable, dataPath)
        to save it to a file
    Requires a starting and an ending URL (in Int), going in decreasing order (eg: 1000, 999, 998, etc)
'''
def imdbscrapper(startURL, endURL):
    # Configuration values for the scrapper
    baseURL         = "https://www.imdb.com/title/tt"       # Base URL for each title
    debugLevel      = 40                                    # 20 will display Info messages, 40 errors
    #logFile         = "/opt/storage/info.log"               # Log output
    counterFile     = "/opt/storage/counter.txt"            # Which ID was last scanned
    reCheckFile     = "/opt/storage/recheck.txt"            # Which IDs to recheck
    moviesFile      = "/opt/storage/movies.csv"             # Where to store movie info
    seriesFile      = "/opt/storage/series.csv"             # Where to store shows/series info

    # Initialize List of lists
    movieTable   = []
    serieTable   = []
    errorTable   = []
    reCheckTable = []
    # Go in descending order from startURL to endURL
    for i in range(startURL, endURL, -1):
        #logging.basicConfig(filename=logFile, level=logging.INFO)
        titleFixed = str(i).zfill(9)               # Adds leading zeros, so that it always has 7 digits
        url        = baseURL + titleFixed + '/'    # String Joins every part of the URL
        dataRow    = []                            # Initializes the dataRow list
        errorRow   = []                            # Initializes the errorRow list
        reCheckRow = []                            # Initializes the reCheckRow list

        # Assume Non Duplicate
        testDuplicate = True
        # Test for Duplicate
        testDuplicate = checkForDuplicate(titleFixed)

        # If a duplicate is found, skip number
        if testDuplicate is False:
            continue
        # While made to wait if 503 code is received (too many requests)
        testNext = False
        while testNext == False:
            try:
                testNext = True
                dataRow.append(titleFixed)
                # Requests, parses and loads into JSON the HTML response
                html = requests.get(url).text
                soup = BeautifulSoup(html, 'html.parser')
                # If Error 503 is found
                if len(soup.findAll(text='Error 503')) > 0:
                    testNext = False
                    print ("Did we just got 503ed? Waiting 60...")
                    sleep(60)


                data = json.loads(soup.find('script', type='application/ld+json').string)

                # If the response is a TVEpisode, just skip the number altogether
                if(data['@type'] == 'TVEpisode'):
                    saveIgnoreToDatabase(titleFixed)
                    continue

                # Gets the desired values from the JSON response
                dataRow.append(data['name'])
                try:
                    dataRow.append(str(data['description']).replace(';', ''))
                except Exception as e:
                    dataRow.append("Description unavailable")
                dataRow.append(url)
                try:
                    dataRow.append(data['genre'])
                except Exception as e:
                    dataRow.append(0)
                try:
                    dataRow.append(data['aggregateRating']['ratingValue'])
                except Exception as e:
                    dataRow.append(0)
                try:
                    dataRow.append(data['aggregateRating']['ratingCount'])
                except Exception as e:
                    dataRow.append(0)
                try:
                    dataRow.append(data['datePublished'])
                except Exception as e:
                    dataRow.append('1000-01-01')

                # Checks if its a movie or a serie/show, and append the list to the list of lists
                if(data['@type'] == 'Movie'):
                    movieTable.append(dataRow)
                if(data['@type'] == 'TVSeries'):
                    serieTable.append(dataRow)
            except Exception as e:
                # Prepares the error string, then append the error list to the list of lists of errors
                #errorMessage = titleFixed + " - " + str(e)
                #errorRow.append(errorMessage)
                #errorTable.append(errorRow)
                # If the error is page not available, append to reCheck list (Performance improvement on rechecks)

                if("NoneType" in str(e)):
                    # [TODO] Page 404 not implemented
                    # If Error 404 is found
                    saveRecheckToDatabase(titleFixed)
                    #testNext = False
                    #print ("Uncaught Error? Waiting 10")
                    #sleep(10)
                    #recheckString = titleFixed + "\n"
                    #reCheckRow.append(recheckString)
                    #reCheckTable.append(reCheckRow)



    # Writes the list of lists to each correct file
    #saveToFile(movieTable, moviesFile)
    #saveToFile(serieTable, seriesFile)
    #saveToFile(errorTable, logFile)
    #saveToFile(reCheckTable, reCheckFile)
    saveToDatabase(movieTable, 'movies')
    saveToDatabase(serieTable, 'series')


def main():
    pass


if __name__ == "__main__":
    main()
