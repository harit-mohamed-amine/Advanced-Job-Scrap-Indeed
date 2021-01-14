import time
from flask import request, jsonify
import requests    
from bs4 import BeautifulSoup as soup    
import re 
import urllib.parse
import operator


URL = "https://www.indeed.com/jobs?q=consultant (data or sql)"

page = requests.get(URL)

#html parsing    
page_soup = soup(page.text, "html.parser")    
    
#grab all divs with a class of result    
results = page_soup.findAll("div", {"class": "result"})      
#initialising variables
listy=[]   
descriptions=[]    

#list of wanted words in the job description
pos = ['etl','cloud'] 
#list of uwanted words in the job description
neg = ['experienced','aws']        

#list of words to exclude from words statistics
words_exclude=['and', 'the', 'you', 'for', 'with', 'our', 'this', 'are', 'job', 'new', 'into', 'other', 'from', 'business', 'company', 'one', 'two', 'tree', 'who', 'that', 'their', 'where', 'please', 'within', 'background', 'individual', 'individuals', 'all', 'join', 'work', 'will', 'your', 'must', 'not', 'have', 'team', 'teams', 'may', 'who', 'candidates', 'candidate', 'opportunity', 'working', 'duties', 'well', 'should', 'has', 'any', 'using', 'various', 'about', 'benefits', 'when', 'use', 'but', 'which', 'within', 'good', 'bad', 'they', 'been', 'why','And/Or','position','such','including','more','role','every','like','make','per','year','require','required']
char_exclude="().,'\"!:"

#looping for each job card
for result in results:
    location = result.findAll('span', {'class':'location'})    
    location_name = location[0].text.strip()  
    
    title = result.a["title"]    
    
    company = result.findAll('span', {'class':'company'})
    company_name = company[0].text.strip()      

    dates = result.findAll('span', {'class':'date'})    
    date = ""    
    if len(dates) != 0:   
        date = dates[0].text.strip()     
        
    salaries = result.findAll('span', {'class':'salaryText'})    
    scraped_salaries = ""    
    if len(salaries) != 0:    
        scraped_salaries = salaries[0].text.strip()    
        
    link = result.a['href']    
    job_link = ("https://www.indeed.com" + link)    
    
    #looking inside each job post
    try:
        page = requests.get(job_link)    
        page_soup = soup(page.text, "html.parser")    
        Description = page_soup.find("div", {"class": "jobsearch-jobDescriptionText"}).text.strip() 
        Description = Description.lower().replace("\n",". ")
        
        #list holding phrases from the description containing wanted and unwanted words
        posNeg = []
        for i in pos:
            index=Description.find(i)
            rindex=Description.rfind(i)
            if index != -1:
                posNeg.append('...'+Description[index-30:index+35]+'...')
            if rindex != -1 and index != rindex:
                posNeg.append('...'+Description[rindex-30:rindex+35]+'...')

        for i in neg:
            index=Description.find(i)
            rindex=Description.rfind(i)
            if index != -1 and i != '' and not(i is None):
                posNeg.append('...'+Description[index-30:index+35]+'...')
            if rindex != -1 and index != rindex and i != '' and not(i is None):
                posNeg.append('...'+Description[rindex-30:rindex+35]+'...')

        posNeg = "	".join(x for x in posNeg)
        
        #cumulating descriptions for words statistics
        descriptions.append(Description)
    except AttributeError:
        continue
        
    #found wanted and unwanted words
    posy = [x for x in pos if(x in Description)]    
    negas = [x for x in neg if(x in Description)]    
    
    #the final informations
    answer = date + ";" + job_link +";" + title + ";" + company_name + ";" + location_name + ";" +  scraped_salaries + ";" + posNeg + "\n"
    
    #calculating score for the current job post
    score = int(len(posy) - len(negas))
    listy.append([answer,score])

#calculating words statistics
flat_list = [item.lower() for i in descriptions for item in i.split() if len(item) > 2 and item not in words_exclude]
for c in char_exclude:
    flat_list = [w.replace(c, "") for w in flat_list]
count_dict = {i:flat_list.count(i) for i in flat_list}
sorted_dict = sorted(count_dict.items(), reverse=True, key=operator.itemgetter(1))
d=[]
for i in sorted_dict:
    d.append(": ".join(str(j) for j in i))
final_most_used=" times. ".join(i for i in d)

#sorting job by score
listy.sort(key=lambda x:x[1],reverse=True)   

#printing results
print(final_most_used.title()+"\n"+"".join([i[0] for i in listy]))

