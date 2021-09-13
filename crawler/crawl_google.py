#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pprint
import time
import argparse
from nltk.tokenize import sent_tokenize
import re
import requests
from bs4 import BeautifulSoup


def get_google_search_page(input_text):
    fox = webdriver.Firefox()
    fox.get("https://www.google.com/")
    search_bar = fox.find_element_by_tag_name("input")
    search_bar.send_keys(input_text)
    search_bar.send_keys(Keys.ENTER)
    time.sleep(2)
    cur_url = fox.current_url
    fox.close()
    fox.quit()
    return cur_url

def get_top_results(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    all_urls = []
    for elems in soup.findAll('h3'):
        for link in soup.findAll('a'):
            url = str(link.get('href'))
            if url.startswith('/url?'):
                all_urls.append(url[7:])
    return all_urls

def filter_duplicate(url_list,max_url=5):
    domain_list = set()
    result = dict()
    blacklist = ["youtube.com"]
    for url in url_list:
        domain = re.findall(r'^https://www.(.*?)/',url) 
        url = re.findall(r'^https://(.*?)&sa',url) # &sa is there for the google rubbish
        if domain != [] and domain[0] not in domain_list and domain[0] not in blacklist:   #it will not check[0] until domain != [] satisfy
            domain_list.add('https://www.'+domain[0])
            result['www.'+domain[0]] = "https://"+url[0]
            if len(domain_list) == max_url:
                break
    return result



def extract_text_elems_from_urls(urls):
    stored_text = dict()
    for url_ in urls.values():
        #print(f'========{url_}===========')
        try: 
            childpage = requests.get(url_)
            childsoup = BeautifulSoup(childpage.content, 'html.parser')
            stored_text[url_] = {'h1':set(),'p':set()}
            for tagment in ['h1','p']:
                    elements = childsoup.findAll(tagment)
                    for element in elements:
                        stored_text[url_][tagment].add(element.text)
        except:
            print(f"ERROR at url {url_}")
            pass
        #print("========================================================")
    return stored_text




def clean_sentence(sent):
    sent = re.sub(f'[\ \r\n]+',' ',sent)
    return sent.lower()


def write_text_dict_to_file(stored_text,outputfile='test.txt'):
    with open(outputfile,'w',encoding='utf-8') as f:
        for url,texts in stored_text.items():
            f.write(f'=========={url}===========\n')
            clean_h1 = []
            f.write(f'<<h1>>\n')
            for h1 in texts['h1']:
                clean_h1 += sent_tokenize(h1)
            for sentence in clean_h1:
                f.write(clean_sentence(sentence))
                f.write('\n')
            f.write(f'<<p>>\n')
            clean_p = []
            for p in texts['p']:
                clean_p += sent_tokenize(p)
            for sentence in clean_p:
                f.write(clean_sentence(sentence))
                f.write('\n')
            f.write('\n\n')
            print(f"Finishing with url: {url}")
    print("Document ready")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("num_pages", help="maximum number of pages crawled",
                        type=int)
    parser.add_argument("input_text", help="the query",
                        type=str)
    parser.add_argument("output", help="the query",
                        type=str)
    args = parser.parse_args()
    
    
    input_text = args.input_text

    print("Getting the google page...")
    gg_url = get_google_search_page(input_text)
    print("Get the first page results....")
    top_search = get_top_results(gg_url) 
    print(f"Duplicate and filter to {args.num_pages} pages...")
    unique_top_search = filter_duplicate(top_search,args.num_pages)
    print("Extracting the h1 and p elements from these pages...")
    stored_text = extract_text_elems_from_urls(unique_top_search)
    print("Writing to file")
    write_text_dict_to_file(stored_text,args.output)
    
if __name__ == "__main__":
    main()
    