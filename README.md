# Upwork parsing

This code make an upwork [search query](https://www.upwork.com/o/jobs/browse/c/data-science-analytics/?page=2&sort=create_time%2Bdesc) to category related jobs (see [the categories list](https://www.upwork.com/o/jobs/browse/)), iterate through result pages and get every job description.
Includes logging.

## Usage

At first we need to crawl all pages from upwork responses. Pages will be stored in ./data/%CURRENT_DATE% directory.

```
python upwork_scraper.py 'Data Science & Analytics'
```

Then we can parse our data to get jobs description. The result - *.csv file in ./.

```
python upwork_parser.py ./data
```
When we run these scripts again, only pages with **new jobs** will be downloaded and processed (it will be faster if only new folder will be passed as argument to parser).

## Dependencies  

```
pip install -r requirements.txt
```

* python 3.6
* numpy 1.13.3
* pandas 0.20.1
* bs4 4.6.0
* tqdm 4.14.0
