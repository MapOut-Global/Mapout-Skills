import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException

op = webdriver.ChromeOptions()
op.add_argument('headless')
op.add_experimental_option('excludeSwitches', ['enable-logging'])
op.add_argument('--no-proxy-server')
op.add_argument("--proxy-server='direct://'")
op.add_argument("--proxy-bypass-list=*")

driver = webdriver.Chrome(r"C:\Users\mapout\Downloads\chromedriver_win32 (1)\chromedriver.exe", options=op)

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}

def get_search_link(keyword,location='india'):

    # this function returns the search link which is created based on the keyword and location entered by user

    keyword1 = keyword.replace(' ','-') # every space in the keyword gets replaced with hyphen in URL(1st repeatition)
    keyword2 = keyword.replace(' ','%2520') # every space in the keyword gets replaced with %2520 in URL(2nd repeatition)
    length = len(location) + len(keyword1) + 1 # this is required in the URL
    link = 'https://www.glassdoor.co.in/Job/{}-{}-jobs-SRCH_IL.0,5_IN115_KO6,{}.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword={}&typedLocation={}&context=Jobs&dropdown=0'.format(location,keyword1,length,keyword2,location)
    return link


def get_job_links(sp):

    # this function extracts the link to all the job postings present on the search job page 

    listings_list = list()

    for a in sp.find_all('a', href=True):
        if "/partner/jobListing.htm?" in a['href']:     
            #print("Found the URL:", a['href'])
            listings_list.append("https://www.glassdoor.com" + a['href'])
            
    return listings_list

def time_breakdown(url):
    
    print('Start of the function',datetime.now())
    
    driver.get(url)
    print('Got the HTML',datetime.now())
    
    #time.sleep(3)
    sp = BeautifulSoup(driver.page_source, 'lxml')
    #print(sp)
    
    print('Starting to search the button',datetime.now())

    button = sp.find_all('span',string='Company') # find if the button exists
    
    if(button): 

        try :
            driver.find_element('xpath',("//*[text()='Company']")).click() # click the button to enter company tab

            print('Found the button and clicked, initiating soup',datetime.now())
            soup = BeautifulSoup(driver.page_source,'html.parser')
            print('Got the new HTML',datetime.now())

            try : 
                print('Searching for industry',datetime.now())
                industry = soup.find('span', {"id" : "primaryIndustry.industryName"}).text
                print('Got the industry',datetime.now())

            except AttributeError :
                print('Could not find industry',datetime.now())
                industry = ''

            try : 
                print('Searching for sector',datetime.now())
                sector = (soup.find('span', {"id" : "primaryIndustry.sectorName"}).text)
                print('Got the sector',datetime.now())

            except AttributeError :
                print('Could not find sector',datetime.now())
                sector = ''

        except NoSuchElementException :
            print('No Button Found',datetime.now())
            industry = ''
            sector = ''


        #print(soup.prettify())
    
    else :
        industry = ''
        sector = ''


    return [industry,sector]


def industry_relation(profession,location='india'):

    industries = []
    sectors = []

    url = get_search_link(profession,location) # get search url
    html = requests.get(url,headers=headers)
    sp = BeautifulSoup(html.content,'lxml')
    listings_list = get_job_links(sp) # get links to all the job postings on search url
    
    # iterate through the job postings to extract necessary details
    for link in set(listings_list):
        #print('entered loop',datetime.now())
        res = requests.get(link,headers=headers)
        redirected_link = res.url 
        print(redirected_link)
        print('started',datetime.now())
        data = time_breakdown(redirected_link)
        #data = time_breakdown(link)
        print('extracted details',datetime.now())
        industries.append(data[0])
        sectors.append(data[1])
        
        print(data)
        #print(listings_list[i])
    print('completed',datetime.now())
    
    return industries,sectors


#trial : 
print(industry_relation('Web Developer'))