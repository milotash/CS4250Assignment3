# Ismael Garcia
# CS4250.01
# Assignment 3 Question 4

from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib.parse import urljoin


# BFS frontier
class Frontier:
    def __init__(self, initial_url):
        self.frontier = [initial_url]
        self.visited = set()

    def next_url(self):
        if not self.frontier:
            return None
        url = self.frontier.pop(0)
        self.visited.add(url)
        return url

    def add_url(self, url):
        if url not in self.visited and url not in self.frontier:
            self.frontier.append(url)

    def done(self):
        return not self.frontier

    def clear_frontier(self):
        self.frontier = []


# Retrieve url - handles full or partial urls
def retrieve_url(base_url, url):
    full_url = urljoin(base_url, url)
    print("Full URL: " + full_url)
    try:
        html = urlopen(full_url).read()
        return html
    except HTTPError as e:
        print(e)
        return None
    except URLError as e:
        print('The server could not be found!')
        return None


# Persist information into collection
def store_page(collection, url, html):
    page = {
        'url': url,
        'html': html.decode('UTF-8')
    }
    collection.insert_one(page)


# Stopping criteria
def target_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    headings = soup.find_all('h1')
    for heading in headings:
        if heading.get_text().strip() == 'Permanent Faculty':
            print("Found target page!")
            return True
    return False


# Find all links in the html
def parse(base_url, html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    return [urljoin(base_url, link['href']) for link in links]


# Crawler to store the url and html every page until the target page is found
def crawler_thread(collection, frontier):
    while not frontier.done():
        url = frontier.next_url()
        html = retrieve_url(url, url)

        store_page(collection, url, html)

        if target_page(html):
            frontier.clear_frontier()
        else:
            links = parse(url, html)
            for link in links:
                frontier.add_url(link)


# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['web_crawler_db']
collection = db['pages']

# Initial URL
initial_url = 'https://www.cpp.edu/sci/computer-science/'

# Initialize frontier with the initial URL
frontier = Frontier(initial_url)

# Run the crawler
crawler_thread(collection, frontier)
