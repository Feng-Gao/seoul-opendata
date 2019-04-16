# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
import scraperwiki
import datetime

import sys

reload(sys)
sys.setdefaultencoding('utf8')

#NOTE that we parse dataproduct and dataapi seperately and the dirty solution is manually replace the url and set index accordingly
#to crawl both product and api, so do not forget to set file writer method to 'a' when you work on api list
base_url = 'http://data.seoul.go.kr/dataList/datasetList.do?pageIndex='
index = 1
#manually check on the website and set the max_index accordingly
max_index = 351

#we need random ua to bypass website security check
ua = UserAgent()
headers = {'User-Agent':ua.random}

problem_url =[]
today_date = datetime.date.today().strftime("%m/%d/%Y")

for i in range(index,max_index+1):
    url = base_url + str(i)
    #print(url)

    result = requests.get(url,headers=headers)
    soup = BeautifulSoup(result.content,features='lxml')
    #fetch all dt blocks and get rid of the first 5 as they are irrelevant
    package_blocks = soup.find_all(attrs={'class':'OneBox_Con'})

    for p in package_blocks:
        #for each package block on the list page, we parse the url to detail page, and package title
        package_url = "http://data.seoul.go.kr/dataList/"+p.dl.a['href']
        package_name = p.find(attrs={'class':'In_Titles'}).span.next.next.strip()
        package_topics = p.find(attrs={'class':'In_Titles'}).span.text.strip()
        #print(package_url)
        #print(package_name)
       
        imgs = p.find(attrs={'class':'In_Ico'}).find_all('img')
        format = []
        for i in imgs:
            format.append(i['src'].split('/')[2].split('.')[0])
        format = '|'.join(format)
        package_format = format

        package_org = p.find(attrs={'class':'In_cont01'}).text.strip()
        package_view = p.find(attrs={'class':'In_cont02'}).span.text.split(':')[1].strip()
        package_desc = '"'+p.find_all(attrs={'class':'In_cont02'})[1].text.strip()+'"'
        try:
            #go to detail page
            result = requests.get(package_url,headers=headers)
            soup = BeautifulSoup(result.content,features='lxml')
            
            package_created = soup.find('span',string='데이터공개일자').next.next.next.text.strip()
            package_frequency = soup.find('span',string='갱신주기').next.next.next.text.strip()
            if soup.find('span',string='데이터수정일자'):
                package_updated = soup.find('span',string='데이터수정일자').next.next.next.text.strip()
            else:
                package_updated = 'MISSING'
            package_tags = '|'.join([x.text for x in soup.find('span',string='태그').parent.find_all('span')[1].find_all('a')])


            #output the result
            #note for tags, it might be splited by , or chinese , or chinese 、
            row = package_url+','+package_name+','+package_desc+','+package_org+','+package_topics\
                    +','+package_tags+','+package_format+','+package_created+','+package_frequency+','+package_view+'\n'
            #print(row)
            package_dict = {
                    'today':today_date,
                    'url':package_url,
                    'name':package_name,
                    'desc':package_desc,
                    'org':package_org,
                    'topics':package_topics,
                    'tags':package_tags,
                    'format':package_format,
                    'created':package_created,
                    'frequency':package_frequency,
                    'updated':package_updated,
                    'view':package_view,
                    
            }
            scraperwiki.sqlite.save(unique_keys=['today','name'],data=package_dict)
            #print('****************end---'+package_name+'---end****************')
        except Exception as ex:
            print(ex)
            print(package_url + ' problem occurs and will re-try')
            problem_url.append({'name':package_name,'topics':package_topics,'url':package_url,'org':package_org,'format':package_format,'view':'package_view,'desc':package_desc})
            continue

print(problem_url)

for p in problem_url:
        #for each package block on the list page, we parse the url to detail page, and package title
        package_url = p['url']
        package_name = p['name']
        package_topics = p['topics']
        #print(package_url)
        #print(package_name)
        
      
        package_format = p['format']

        package_org = p['org']
        package_view = p['view']
        package_desc = p['desc']
        try:
            #go to detail page
            result = requests.get(package_url,headers=headers)
            soup = BeautifulSoup(result.content,features='lxml')

            package_created = soup.find('span',string='데이터공개일자').next.next.next.text.strip()
            package_frequency = soup.find('span',string='갱신주기').next.next.next.text.strip()
            package_tags = '|'.join([x.text for x in soup.find('span',string='태그').parent.find_all('span')[1].find_all('a')])
            if soup.find('span',string='데이터수정일자'):
                package_updated = soup.find('span',string='데이터수정일자').next.next.next.text.strip()
            else:
                package_updated = 'MISSING'

            #output the result
            #note for tags, it might be splited by , or chinese , or chinese 、
            row = package_url+','+package_name+','+package_desc+','+package_org+','+package_topics\
                    +','+package_tags+','+package_format+','+package_created+','+package_frequency+','+package_updated+','+package_view+'\n'
            #print(row)
            package_dict = {
                    'today':today_date,
                    'url':package_url,
                    'name':package_name,
                    'desc':package_desc,
                    'org':package_org,
                    'topics':package_topics,
                    'tags':package_tags,
                    'format':package_format,
                    'created':package_created,
                    'frequency':package_frequency,
                    'updated':package_updated,
                    'view':package_view,
                    
            }
            scraperwiki.sqlite.save(unique_keys=['today','name'],data=package_dict)
            #print('****************end---'+package_name+'---end****************')
        except Exception as ex:
            print(ex)
            print(package_url + ' problem occurs and will re-try')
            problem_url.append({'name':package_name,'topics':package_topics,'url':package_url,'org':package_org,'format':package_format,'view':'package_view,'desc':package_desc})
            continue
