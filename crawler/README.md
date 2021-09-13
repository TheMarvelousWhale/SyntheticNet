# Python Google Search results crawler

The script attempts to crawl the pages from google top results in order to get more information about certain concepts

requirements:
    python 3 in anaconda env
    selenium 
    nltk (for sentence tokenizer)
    BeautifulSoup4
    Firefox (can be adapted for other Selenium drivers)

Please refer to crawl_google.yml
How to run:
    python crawl_google.py \[num_pages_to_crawl\] \[input text\] \[output file\]
  e.g:
    python crawl_google.py 10 moderna moderna.txt 
    
The script will:
* open a selenium marionette and get the google front page html 
* beautiful soup will get the top results' url (with filters)
* requests each of the url and get their h1 (likely to be title) and p elements
* write results to file

Notes: I blacklist youtube as there's not very informative text
