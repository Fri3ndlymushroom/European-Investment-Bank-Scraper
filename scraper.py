from bs4 import BeautifulSoup
import time

# selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService

# chrome
from webdriver_manager.chrome import ChromeDriverManager
service = ChromeService(executable_path=ChromeDriverManager().install())

# get code
url = "https://www.eib.org/en/projects/all/index.htm?q=&sortColumn=statusDate&sortDir=desc&pageNumber=0&itemPerPage=9&pageable=false&language=EN&defaultLanguage=EN&=&or=true&yearFrom=2018&yearTo=2022&status=approved&status=signed&orStatus=true&orRegions=true&orCountries=true&orSectors=true"
browser = webdriver.Chrome(service=service)
browser.get(url)

time.sleep(0.5)

html = browser.page_source

# refactor
soup = BeautifulSoup(html, 'html.parser')

articles = soup.find_all("article")

# remove header
del articles[0]
links = []

for article in articles:
    links.append("https://www.eib.org"+article.a.get('href'))

links = ["https://www.eib.org/en/projects/all/20210565"]


class Project:
    def __init__(self):
        print("inited")


data = []

for link in links:

    browser.get(link)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    currentProject = Project()
    currentProject.link = link



    # summary sheet
    summary = soup.find_all(
        "div", {"id": "pipeline"})[0]

    batch = summary.find_all(
        "div", {"class": "eib-list__column"})

    

    i = 0
    for div in batch:
        batch[i] = div.text
        i += 1
    print(i)

    currentProject.release_date = batch[1]
    currentProject.status = batch[4]
    currentProject.reference = batch[5]
    currentProject.project_name = batch[8]
    currentProject.promoter = batch[9]
    currentProject.total_cost = batch[13]
    currentProject.location = batch[16]
    currentProject.sector = batch[17]
    currentProject.description = batch[20]
    currentProject.objectives = batch[21]
    currentProject.environmental_aspects = batch[24]
    currentProject.procurement = batch[25]


    # links
    batch = soup.find_all(
        "div", {"id": "loan-relatedDocuments"})

    if(len(batch) > 1):
        batch = batch[1]
        sections = batch.find_all(
            "div", {"class": "eib-list__row"})

        links_bundle = []
        for section in sections:
            links_bundle.append(section.find_all("a")[1])

        links = []
        for link in links_bundle:
            links.append("https://www.eib.org"+link.get('href'))

        links_title = []
        for link in links_bundle:
            links_title.append(link.text)

        currentProject.other_links = links
        currentProject.other_links_title = links_title
    else:
        currentProject.other_links = []
        currentProject.other_links_title = []
    print(currentProject.__dict__)

    #signatures
    has_signature_tab = len(soup.find_all("div", {"id": "loan"})) > 0

    if (has_signature_tab):
        summary = soup.find_all(
        "div", {"id": "loan"})[0]

        batch = summary.find_all(
            "div", {"class": "eib-list__column"})
 
        i = 0
        for div in batch:
            batch[i] = div.text
            print(i)
            print(div.text)
            i += 1
        
        currentProject.amount = batch[1]
        currentProject.countries = batch[4]
        currentProject.sectors = batch[5]

    else:
        currentProject.amount = ""
        currentProject.countries = ""
        currentProject.sectors = ""





browser.close()
browser.quit()
