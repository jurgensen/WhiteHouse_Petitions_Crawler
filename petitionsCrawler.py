#!/usr/bin/python2.7

from lxml import html
from requests import get as rget
from datetime import datetime
from time import sleep as sleep
import csv



start_url = "https://petitions.whitehouse.gov/petitions"
retrieval_time = datetime.today()

all_petitions = []
all_titles = []
all_links = []
all_signatures = []

def get_page(url_to_follow):
    page = rget(url_to_follow, timeout=(0.1, 5))
    temp_tree = html.fromstring(page.content)
    return temp_tree

def process_page(tree_from_page):
    title_list = tree_from_page.xpath("//h3/a/text()")
    list_of_links = tree_from_page.xpath('//h3/a')
    signatures_list = tree_from_page.xpath('//span[@class="signatures-number"]/text()')
    try:
        next_as_element = tree_from_page.xpath('//div[@class="page-load-next"]/a')
        next = next_as_element[0].attrib['href']
    except:
        next = ''
    return title_list,list_of_links, signatures_list, next

def get_links(link_list):
    prefix =  'https://petitions.whitehouse.gov'
    temp_list = []
    for x in link_list:
        temp_list.append(prefix+x.attrib['href'])
    return temp_list

def transfer_to_global_lists(temp_tree):
    [t,l,s,n] = process_page(temp_tree)
    link_list = []
    for x in get_links(l):
        link_list.append(x)

    x = 0
    while x < len(t):
        all_titles.append(t[x])
        all_links.append(link_list[x])
        all_signatures.append(s[x])
        x += 1

    if len(n) > 0:
        sleep(2.0)
        tree = get_page('https://petitions.whitehouse.gov'+n)
        transfer_to_global_lists(tree)


#start process using the first petitions page
tree = get_page(start_url)
transfer_to_global_lists(tree)

#populate final list with info from all of the petitions
x = 0
while x < len(all_titles):
    temp_petition = [all_titles[x],all_links[x],all_signatures[x]]
    all_petitions.append(temp_petition)
    x += 1

#when writing, update the header date with the time of page reading
#format year_month_day_HR:MN:SEC
today = retrieval_time.strftime('%Y_%m_%d_%H:%M:%S')
today_for_name = retrieval_time.strftime('%Y_%m_%d__%H_%M_%S')
filename = '/home/jurgensen/petitionsCrawler/whpetitions_'+today_for_name+'.tsv'
outputFile = open(filename, 'w')
#print(outputFile)
csvWriter = csv.writer(outputFile, delimiter = '\t')
for x in all_petitions:
    row = [i.encode('utf-8') for i in x]
    csvWriter.writerow(row)
outputFile.close()
