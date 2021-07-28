FROM python:3.9-alpine3.13

RUN mkdir /opt/storage
WORKDIR /opt/imdbscrapper

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/scrapper/ .

CMD ["python", "-u", "/opt/imdbscrapper/scrapper.py"]
