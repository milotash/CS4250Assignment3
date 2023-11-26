# Ismael Garcia
# CS4250.01
# Assignment 3 Question 5

from bs4 import BeautifulSoup
from pymongo import MongoClient
import re

# Mongo DB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['web_crawler_db']
pages = db['pages']
professors = db['professors']

# Query the Mongo DB to find the target page
target_page = db.pages.find_one( {'url': 'https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml'})
print(target_page)
print()

# Create a BeautifulSoup object with the target page's html content
html = target_page['html']
soup = BeautifulSoup(html, 'html.parser')


# Persist information into collection
def store_prof(collection, name, title, office, email, website):
    professor = {
        'name': name,
        'title': title,
        'office': office,
        'email': email,
        'website': website
    }
    collection.insert_one(professor)

# Find all div elements with class "clearfix" (each div represents a professor)
profList = soup.find_all('div', class_='clearfix')

# Loop through each professor div
for prof in profList:
    try:
        # Extract information from the div
        name = prof.find('h2').get_text()
        print("name: " + name)
        title = prof.find('strong', string=re.compile('.*Title.*')).next_sibling.get_text()
        print("title: " + title)
        office = prof.find('strong', string=re.compile('.*Office.*')).next_sibling.get_text()
        print("office: " + office)
        email = prof.find('strong', string=re.compile('.*Email.*')).find_next('a').get('href').split(':')[1]
        print("email: " + email)
        website = prof.find('strong', string= re.compile('.*Web.*')).find_next('a').get('href')
        print("website: " + website)
        print()

        # Persist professor information into the collection called 'professors'
        store_prof(professors, name, title, office, email, website)
    except AttributeError:
        continue
