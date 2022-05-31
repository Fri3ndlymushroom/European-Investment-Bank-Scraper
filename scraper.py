from bs4 import BeautifulSoup
import time
import re
import xlsxwriter


# selenium
from selenium import webdriver

from selenium.webdriver.chrome.service import Service as ChromeService

# chrome
from webdriver_manager.chrome import ChromeDriverManager
service = ChromeService(executable_path=ChromeDriverManager().install())
browser = webdriver.Chrome(service=service)


def goToPage(url):
    browser.get(url)
    time.sleep(1)


def statusPrint(message):
    print("-------------------------------------")
    print(message)
    print("-------------------------------------")


# get covid results
statusPrint("Collecting all Covid Projects")

covid_url = "https://www.eib.org/en/about/initiatives/covid-19-response/financing.htm?q=&sortColumn=name&sortDir=asc&pageNumber=0&itemPerPage=25&pageable=true&language=EN&defaultLanguage=EN&=&or=true&orCountries=true&orSectors=true&status=approved&status=signed&orStatus=true#financed-projects"
goToPage(covid_url)

el = browser.find_element_by_id(
    'show-entries').find_elements_by_tag_name('option')[4].click()
time.sleep(5)

html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')


covid_list = soup.find("div", {"id": "mainlist"})
covid_articles = covid_list.find_all("article")
del covid_articles[0]
covid_links = []

for covid_article in covid_articles:
    covid_links.append("https://www.eib.org/" +
                       covid_article.find("h3").a.get('href'))

covid_references = []

k = 0
for covid_link in covid_links:
    statusPrint("Scraping Covid Project "+str(k+1)+"/" + str(len(covid_links)))

    goToPage(covid_link)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    covid_references.append(
        soup.find('div', {"class": "pipeline-ref"}).find_all("span")[1].text)
    k+= 1


# get all projects
statusPrint("Collecting all Projects")

url = "https://www.eib.org/en/projects/all/index.htm?q=&sortColumn=statusDate&sortDir=desc&pageNumber=0&itemPerPage=9&pageable=false&language=EN&defaultLanguage=EN&=&or=true&yearFrom=2018&yearTo=2022&status=approved&status=signed&orStatus=true&orRegions=true&orCountries=true&orSectors=true"
goToPage(url)

el = browser.find_element_by_id(
    'show-entries').find_elements_by_tag_name('option')[4].click()
time.sleep(20)

html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')


articles = soup.find_all("article")
del articles[0]
links = []

for article in articles:
    links.append("https://www.eib.org"+article.a.get('href'))


# search
class Project:
    def __init__(self, index):
        self.index = index


raw_data = []

y = 0
for link in links:
    statusPrint("Scraping Project "+str(y+1)+"/" + str(len(links)))

    browser.get(link)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    currentProject = Project(y)
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

    # signatures
    has_signature_tab = len(soup.find_all("div", {"id": "loan"})) > 0

    if (has_signature_tab):
        summary = soup.find_all(
            "div", {"id": "loan"})[0]

        batch = summary.find_all(
            "div", {"class": "eib-list__column"})

        i = 0
        for div in batch:
            batch[i] = div.text
            i += 1

        currentProject.amount = batch[1]
        currentProject.countries = batch[4]
        currentProject.sectors = batch[5]

    else:
        currentProject.amount = ""
        currentProject.countries = ""
        currentProject.sectors = ""

    currentProject.covid_project = currentProject.reference in covid_references

    raw_data.append(currentProject)
    y += 1


browser.close()
browser.quit()


statusPrint("Refactoring Projects")

class Refactored:
    def __init__(self):
        0


refactored_data = []


# refactor
for project in raw_data:

    current = Refactored()

    # index
    current.index = project.index

    # link
    current.link = project.link

    # release date
    current.release_date = project.release_date.strip()

    # status
    cleaned = project.status.strip()
    current.status = re.search("(.*?)(?= \|)", cleaned)[0]
    current.status_date = re.search("(?<=\| ).*$", cleaned)[0]

    # reference
    current.reference = project.reference.strip()

    # project name
    current.project_name = project.project_name.strip()
    # promoter
    current.promoter = project.promoter.strip()

    # total cost
    cleaned = project.total_cost.strip()
    parts = re.findall("[^ ]*", cleaned)
    current.total_cost_currency = parts[0]
    current.total_cost_amount = parts[2]
    current.total_cost_scale = parts[4]

    # location
    current.location = project.location.strip()

    # description

    current.description = project.description.strip()


    # objectives
    current.objectives = project.objectives.strip()

    # environmental aspects
    current.environmental_aspects = project.environmental_aspects.strip()

    # procurement
    current.procurement = project.procurement.strip()

    # other links
    linkstring = ""

    i = 0
    for link in project.other_links:
        linkstring = linkstring + \
            project.other_links_title[i] + ": " + link + " || "
        i += 1

    current.other_links = linkstring

    # amount
    cleaned = project.amount.strip()
    parts = re.findall("[^ ]*", cleaned)
    current.amount_currency = parts[0]
    current.amount = parts[2]

    # counries
    cleaned = str(project.countries)
    lines = re.findall("(?<=\\n)(.*?)(?=\\n)", cleaned)
    content_lines = []

    for line in lines:
        if line != "":
            content_lines.append(line)

    current.countries_1 = content_lines[0]
    current.countries_1_currency = re.findall(
        "(?<=: )(.*?)(?= )", content_lines[1])[0]
    currency_and_amount = re.findall("(?<= )(.+?)(?=$)", content_lines[1])
    current.countries_1_amount = re.findall(
        "(?<= )(.+?)(?=$)", currency_and_amount[0])[0]

    if len(content_lines) > 2:
        current.countries_2 = content_lines[2]
        current.countries_2_currency = re.findall(
            "(?<=: )(.*?)(?= )", content_lines[3])[0]
        currency_and_amount = re.findall("(?<= )(.+?)(?=$)", content_lines[3])
        current.countries_2_amount = re.findall(
            "(?<= )(.+?)(?=$)", currency_and_amount[0])[0]
    else:
        current.countries_2 = ""
        current.countries_2_currency = ""
        current.countries_2_amount = ""

    if len(content_lines) > 4:
        current.countries_3 = content_lines[4]
        current.countries_3_currency = re.findall(
            "(?<=: )(.*?)(?= )", content_lines[5])[0]
        currency_and_amount = re.findall("(?<= )(.+?)(?=$)", content_lines[5])
        current.countries_3_amount = re.findall(
            "(?<= )(.+?)(?=$)", currency_and_amount[0])[0]
    else:
        current.countries_3 = ""
        current.countries_3_currency = ""
        current.countries_3_amount = ""

    # sectors

    # sector
    cleaned = str(project.sector)
    lines = re.findall("(?<=\\n)(.*?)(?=\\n)", cleaned)
    sector_descriptions = []

    for line in lines:
        if line != "":
            sector_descriptions.append(line)

    cleaned = str(project.sectors)
    lines = re.findall("(?<=\\n)(.*?)(?=\\n)", cleaned)
    content_lines = []

    for line in lines:
        if line != "":
            content_lines.append(line)

    current.sectors_1 = content_lines[0]
    current.sectors_1_currency = re.findall(
        "(?<=: )(.*?)(?= )", content_lines[1])[0]
    currency_and_amount = re.findall("(?<= )(.+?)(?=$)", content_lines[1])
    current.sectors_1_amount = re.findall(
        "(?<= )(.+?)(?=$)", currency_and_amount[0])[0]
    current.sectors_1_description = re.findall(
        "(?<=- )(.+?)(?=$)", sector_descriptions[1])[0]

    if len(content_lines) > 2:
        current.sectors_2 = content_lines[2]
        current.sectors_2_currency = re.findall(
            "(?<=: )(.*?)(?= )", content_lines[3])[0]
        currency_and_amount = re.findall("(?<= )(.+?)(?=$)", content_lines[3])
        current.sectors_2_amount = re.findall(
            "(?<= )(.+?)(?=$)", currency_and_amount[0])[0]
        current.sectors_2_description = re.findall(
            "(?<=- )(.+?)(?=$)", sector_descriptions[3])[0]
    else:
        current.sectors_2 = ""
        current.sectors_2_currency = ""
        current.sectors_2_amount = ""
        current.sectors_2_description = ""

    if len(content_lines) > 4:
        current.sectors_3 = content_lines[4]
        current.sectors_3_currency = re.findall(
            "(?<=: )(.*?)(?= )", content_lines[5])[0]
        currency_and_amount = re.findall("(?<= )(.+?)(?=$)", content_lines[5])
        current.sectors_3_amount = re.findall(
            "(?<= )(.+?)(?=$)", currency_and_amount[0])[0]
        current.sectors_3_description = re.findall(
            "(?<=- )(.+?)(?=$)", sector_descriptions[5])[0]
    else:
        current.sectors_3 = ""
        current.sectors_3_currency = ""
        current.sectors_3_amount = ""
        current.sectors_3_description = ""

    current.covid_project = project.covid_project

    refactored_data.append(current)

statusPrint("Writing to excel")

workbook = xlsxwriter.Workbook('results.xlsx')
worksheet = workbook.add_worksheet()

i = 1
for project in refactored_data:
    worksheet.write('A'+str(i), project.link)
    worksheet.write('B'+str(i), project.release_date)
    worksheet.write('C'+str(i), project.status)
    worksheet.write('D'+str(i), project.status_date)
    worksheet.write('E'+str(i), project.reference)
    worksheet.write('F'+str(i), project.project_name)
    worksheet.write('G'+str(i), project.promoter)
    worksheet.write('H'+str(i), project.total_cost_currency)
    worksheet.write('I'+str(i), project.total_cost_amount)
    worksheet.write('J'+str(i), project.total_cost_scale)
    worksheet.write('K'+str(i), project.location)
    worksheet.write('L'+str(i), project.description)
    worksheet.write('M'+str(i), project.objectives)
    worksheet.write('N'+str(i), project.environmental_aspects)
    worksheet.write('O'+str(i), project.procurement)
    worksheet.write('P'+str(i), project.other_links)
    worksheet.write('Q'+str(i), project.amount_currency)
    worksheet.write('R'+str(i), project.amount)
    worksheet.write('S'+str(i), project.countries_1)
    worksheet.write('T'+str(i), project.countries_1_currency)
    worksheet.write('U'+str(i), project.countries_1_amount)
    worksheet.write('V'+str(i), project.countries_2)
    worksheet.write('W'+str(i), project.countries_2_currency)
    worksheet.write('X'+str(i), project.countries_2_amount)
    worksheet.write('Y'+str(i), project.countries_3)
    worksheet.write('Z'+str(i), project.countries_3_currency)
    worksheet.write('AA'+str(i), project.countries_3_amount)
    worksheet.write('AB'+str(i), project.sectors_1)
    worksheet.write('AC'+str(i), project.sectors_1_currency)
    worksheet.write('AD'+str(i), project.sectors_1_amount)
    worksheet.write('AE'+str(i), project.sectors_1_description)
    worksheet.write('AF'+str(i), project.sectors_2)
    worksheet.write('AG'+str(i), project.sectors_2_currency)
    worksheet.write('AH'+str(i), project.sectors_2_amount)
    worksheet.write('AI'+str(i), project.sectors_2_description)
    worksheet.write('AJ'+str(i), project.sectors_3)
    worksheet.write('AK'+str(i), project.sectors_3_currency)
    worksheet.write('AL'+str(i), project.sectors_3_amount)
    worksheet.write('AM'+str(i), project.sectors_3_description)
    worksheet.write('AN'+str(i), project.covid_project)

    i += 1


workbook.close()

statusPrint("Finsihed")
