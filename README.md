# imdbscrapper
Scrapper to get movies information from IMDB, indexing it into movies and shows, with rating, release date, and a few more information.

### Situation
Finding movies / shows to watch, based on ratings and release date.
This search and notes would have to be done manually.


### Task
Create a way to automatically index entries from movies (IMDB), so they can be searched and filtered afterwards via common software (Spreadsheet)

### Action
- Just the scrap data
[IMDBScrap](https://github.com/zebrajr/imdbscrap)

- With Docker

```sh
docker build -t yourUser/yourPackage:yourVersion .
```

- Directly

> Install the requirements described in requirements.txt (pip3 install -r requirements.txt)
> Create the folder structure or edit the settings in the main script
```sh
python3 scrapper.yml
```
### Result
| File | Content |
| ------ | ------ |
| movies.csv | CSV file with all movies indexed |
| series.csv | CSV file with all shows indexed |
| info.log | Any errors occured. Change the debug level if you want to log info messages |
| counter.txt | The last indexed url. Needed to continue in case the script is interrupted |

### Note

### ToDo
- Dont input duplicates into dataTable
- Add Error Handling in case Internet is not available
- Add possibility to re-index failed entries (to go though the indexer faster when a new movie/show is added)
- Add Multithreading



Ps.: Feel free to improve :)


## Some Statistics
<img src="https://img.shields.io/github/license/zebrajr/imdbscrapper?logo=github"><img src="https://img.shields.io/github/forks/zebrajr/imdbscrapper?logo=github"><img src="https://img.shields.io/github/stars/zebrajr/imdbscrapper?logo=github">
<br>
<img src="https://img.shields.io/github/last-commit/zebrajr/imdbscrapper?logo=gitfs"><img src="https://img.shields.io/maintenance/yes/2021">
<br>
<img src="https://img.shields.io/github/repo-size/zebrajr/imdbscrapper?logo=files"><img src="https://img.shields.io/tokei/lines/github/zebrajr/imdbscrapper?logo=files">
<br>
<img src="https://img.shields.io/github/issues-raw/zebrajr/imdbscrapper?logo=gitbook"><img src="https://img.shields.io/github/issues-closed-raw/zebrajr/imdbscrapper?logo=gitbook">
<br>
<img src="https://img.shields.io/github/issues-pr-raw/zebrajr/imdbscrapper?logo=git"><img src="https://img.shields.io/github/issues-pr-closed-raw/zebrajr/imdbscrapper?logo=git">
