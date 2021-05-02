# imdbscrapper
Scrapper to get movies information from IMDB, indexing it into movies and shows, with rating, release date, and a few more information.

### Situation
Finding movies / shows to watch, based on ratings and release date.
This search and notes would have to be done manually.


### Task
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
- Add Error Handling in case Internet goes is not available
