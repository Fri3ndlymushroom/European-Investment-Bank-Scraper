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

TEST_MODE = False


def goToPage(url):
    browser.get(url)
    time.sleep(0.7)  # change this to edit delay between page loads


def statusPrint(message):
    print(message)
    print("-------------------------------------")


def returnIfDefined(value):
    if value is None:
        return ""
    else:
        return value


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

statusPrint("Collecting Covid project references")

for covid_link in covid_links:
    covid_references.append(re.findall("(?<=all/).*$", covid_link)[0])

print(covid_references)
# get all projects
statusPrint("Collecting all Projects")

url = "https://www.eib.org/en/projects/all/index.htm?q=&sortColumn=statusDate&sortDir=desc&pageNumber=0&itemPerPage=9&pageable=false&language=EN&defaultLanguage=EN&=&or=true&yearFrom=2018&yearTo=2022&status=approved&status=signed&orStatus=true&orRegions=true&orCountries=true&orSectors=true"
goToPage(url)
if not TEST_MODE:
    el = browser.find_element_by_id(
        'show-entries').find_elements_by_tag_name('option')[4].click()

if not TEST_MODE:
    time.sleep(20)
else:
    time.sleep(1)

html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')


articles = soup.find_all("article")
del articles[0]
links = []

l = 0
for article in articles:
    statusPrint("Collecting Covid Project https://www.eib.org" +
                article.a.get('href') + " || " + str(l+1) + "/" + str(len(articles)))

    links.append("https://www.eib.org"+article.a.get('href'))
    l += 1


# search
class Project:
    def __init__(self, index):
        self.index = index


raw_data = []

if TEST_MODE:
    links = ["https://www.eib.org/en/projects/all/20210540", "https://www.eib.org/en/projects/all/20210690",
             "https://www.eib.org/en/projects/all/20210768", "https://www.eib.org/en/projects/all/20210540", "https://www.eib.org/en/projects/all//20210116", "https://www.eib.org/en/projects/all/20210604", "https://www.eib.org/en/projects/all/20200045", "https://www.eib.org/en/projects/all/20200483"]

y = 0
for link in links:
    statusPrint("Scraping Project " + link + " || " +
                str(y+1) + "/" + str(len(links)))

    browser.get(link)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    currentProject = Project(y)
    currentProject.link = link

    # summary sheet
    found_summary_sheet = False
    try:
        summary = soup.find_all(
            "div", {"id": "pipeline"})[0]

        batch = summary.find_all(
            "div", {"class": "eib-list__column"})
        i = 0
        for div in batch:
            batch[i] = div.text
            i += 1

        found_summary_sheet = True
    except:
        found_summary_sheet = False

    if (found_summary_sheet):
        try:
            currentProject.release_date = returnIfDefined(batch[1])
            currentProject.status = returnIfDefined(batch[4])
            currentProject.reference = returnIfDefined(batch[5])
            currentProject.project_name = returnIfDefined(batch[8])
            currentProject.promoter = returnIfDefined(batch[9])
            currentProject.proposed = returnIfDefined(batch[12])
            currentProject.total_cost = returnIfDefined(batch[13])
            currentProject.location = returnIfDefined(batch[16])
            currentProject.sector = returnIfDefined(batch[17])
            currentProject.description = returnIfDefined(batch[20])
            currentProject.objectives = returnIfDefined(batch[21])


            AdditionalityAndImpactOffset = 0
            if batch[22].strip() == "Additionality and Impact":
                AdditionalityAndImpactOffset = 2
                currentProject.additionality_and_impact = returnIfDefined(
                    batch[23])

            currentProject.environmental_aspects = returnIfDefined(
                batch[24 + AdditionalityAndImpactOffset])
            currentProject.procurement = returnIfDefined(
                batch[25 + AdditionalityAndImpactOffset])
        except:
            x = 1

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

        other_links = []
        for link in links_bundle:
            other_links.append("https://www.eib.org"+link.get('href'))

        links_title = []
        for link in links_bundle:
            links_title.append(link.text)

        currentProject.other_links = other_links
        currentProject.other_links_title = links_title
    else:
        currentProject.other_links = []
        currentProject.other_links_title = []

    # signatures
    has_signature_tab = len(soup.find_all("div", {"id": "loan"})) > 0

    if (has_signature_tab):
        try:
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
        except:
            currentProject.amount = "N/A"
            currentProject.countries = "N/A"
            currentProject.sectors = ""
    else:
        currentProject.amount = "N/A"
        currentProject.countries = "N/A"
        currentProject.sectors = ""

    try:
        currentProject.covid_project = currentProject.reference.strip() in covid_references
    except:
        currentProject.covid_project = "N/A"

    raw_data.append(currentProject)
    y += 1


browser.close()
browser.quit()


statusPrint("Formating Projects")


class Refactored:
    def __init__(self):
        0


refactored_data = []


# refactor
n = 0
for project in raw_data:

    statusPrint("Formating Project" + project.link +
                " || " + str(n+1) + "/" + str(len(raw_data)))

    current = Refactored()

    # index
    current.index = project.index

    # link
    current.link = project.link

    # release date
    try:
        current.release_date = project.release_date.strip()
    except:
        current.release_date = "N/A"

    # status
    try:
        cleaned = project.status.strip()
        current.status = re.search("(.*?)(?= \|)", cleaned)[0]
        current.status_date = re.search("(?<=\| ).*$", cleaned)[0]
    except:
        current.status = "N/A"
        current.status_date = "N/A"

    # reference
    try:
        current.reference = project.reference.strip()
    except:
        current.reference = "N/A"

    # project name
    try:
        current.project_name = project.project_name.strip()
    except:
        current.project_name = "N/A"
    # promoter
    try:
        current.promoter = project.promoter.strip()
    except:
        current.promoter = "N/A"

    # proposed
    try:
        cleaned = project.proposed.strip()
        parts = re.findall("[^ ]*", cleaned)
        current.proposed_currency = parts[0]
        current.proposed_amount = parts[2]
        current.proposed_scale = parts[4]
    except:
        current.proposed_currency = "N/A"
        current.proposed_amount = "N/A"
        current.proposed_scale = "N/A"

    # total cost
    try:
        cleaned = project.total_cost.strip()
        parts = re.findall("[^ ]*", cleaned)
        current.total_cost_currency = parts[0]
        current.total_cost_amount = parts[2]
        current.total_cost_scale = parts[4]
    except:
        current.total_cost_currency = "N/A"
        current.total_cost_amount = "N/A"
        current.total_cost_scale = "N/A"

    # location
    try:
        current.location = project.location.strip()
    except:
        current.location = "N/A"

    # description
    try:
        current.description = project.description.strip()
    except:
        current.description = "N/A"

    # objectives
    try:
        current.objectives = project.objectives.strip()
    except:
        current.objectives = "N/A"
    # additionality and impact
    try:
        current.additionality_and_impact = project.additionality_and_impact.strip()
    except:
        current.additionality_and_impact = "N/A"
    # environmental aspects
    try:
        current.environmental_aspects = project.environmental_aspects.strip()
    except:
        current.environmental_aspects = "N/A"

    # procurement
    try:
        current.procurement = project.procurement.strip()
    except:
        current.procurement = "N/A"

    # other links
    try:
        linkstring = ""

        i = 0
        for link in project.other_links:
            linkstring = linkstring + \
                project.other_links_title[i] + ": " + link + " || "
            i += 1

        current.other_links = linkstring
    except:
        current.other_links = "N/A"

    # amount
    try:
        cleaned = project.amount.strip()
        parts = re.findall("[^ ]*", cleaned)
        current.amount_currency = parts[0]
        current.amount = parts[2]
    except:
        current.amount_currency = "N/A"
        current.amount = "N/A"

    # counries
    try:
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
            currency_and_amount = re.findall(
                "(?<= )(.+?)(?=$)", content_lines[3])
            current.countries_2_amount = re.findall(
                "(?<= )(.+?)(?=$)", currency_and_amount[0])[0]
        else:
            current.countries_2 = "N/A"
            current.countries_2_currency = "N/A"
            current.countries_2_amount = "N/A"

        if len(content_lines) > 4:
            current.countries_3 = content_lines[4]
            current.countries_3_currency = re.findall(
                "(?<=: )(.*?)(?= )", content_lines[5])[0]
            currency_and_amount = re.findall(
                "(?<= )(.+?)(?=$)", content_lines[5])
            current.countries_3_amount = re.findall(
                "(?<= )(.+?)(?=$)", currency_and_amount[0])[0]
        else:
            current.countries_3 = "N/A"
            current.countries_3_currency = "N/A"
            current.countries_3_amount = "N/A"

        if len(content_lines) > 6:
            current.countries_4 = content_lines[6]
            current.countries_4_currency = re.findall(
                "(?<=: )(.*?)(?= )", content_lines[7])[0]
            currency_and_amount = re.findall(
                "(?<= )(.+?)(?=$)", content_lines[7])
            current.countries_4_amount = re.findall(
                "(?<= )(.+?)(?=$)", currency_and_amount[0])[0]
        else:
            current.countries_4 = "N/A"
            current.countries_4_currency = "N/A"
            current.countries_4_amount = "N/A"

        if len(content_lines) > 8:
            current.countries_5 = content_lines[8]
            current.countries_5_currency = re.findall(
                "(?<=: )(.*?)(?= )", content_lines[9])[0]
            currency_and_amount = re.findall(
                "(?<= )(.+?)(?=$)", content_lines[9])
            current.countries_5_amount = re.findall(
                "(?<= )(.+?)(?=$)", currency_and_amount[0])[0]
        else:
            current.countries_5 = "N/A"
            current.countries_5_currency = "N/A"
            current.countries_5_amount = "N/A"

        if len(content_lines) > 10:
            current.countries_6 = content_lines[10]
            current.countries_6_currency = re.findall(
                "(?<=: )(.*?)(?= )", content_lines[11])[0]
            currency_and_amount = re.findall(
                "(?<= )(.+?)(?=$)", content_lines[11])
            current.countries_6_amount = re.findall(
                "(?<= )(.+?)(?=$)", currency_and_amount[0])[0]
        else:
            current.countries_6 = "N/A"
            current.countries_6_currency = "N/A"
            current.countries_6_amount = "N/A"

        if len(content_lines) > 12:
            current.countries_7 = content_lines[12]
            current.countries_7_currency = re.findall(
                "(?<=: )(.*?)(?= )", content_lines[13])[0]
            currency_and_amount = re.findall(
                "(?<= )(.+?)(?=$)", content_lines[13])
            current.countries_7_amount = re.findall(
                "(?<= )(.+?)(?=$)", currency_and_amount[0])[0]
        else:
            current.countries_7 = "N/A"
            current.countries_7_currency = "N/A"
            current.countries_7_amount = "N/A"
    except:
        except_value = "N/A"
        if project.countries == "":
            except_value = "N/A"

        current.countries_1 = except_value
        current.countries_1_currency = except_value
        current.countries_1_amount = except_value
        current.countries_2 = except_value
        current.countries_2_currency = except_value
        current.countries_2_amount = except_value
        current.countries_3 = except_value
        current.countries_3_currency = except_value
        current.countries_3_amount = except_value
        current.countries_4 = except_value
        current.countries_4_currency = except_value
        current.countries_4_amount = except_value
        current.countries_5 = except_value
        current.countries_5_currency = except_value
        current.countries_5_amount = except_value
        current.countries_6 = except_value
        current.countries_6_currency = except_value
        current.countries_6_amount = except_value
        current.countries_7 = except_value
        current.countries_7_currency = except_value
        current.countries_7_amount = except_value
        

    # sectors
    current.sectors_1 = "N/A"
    current.sectors_1_currency = "N/A"
    current.sectors_1_amount = "N/A"
    current.sectors_1_description = "N/A"
    current.sectors_2 = "N/A"
    current.sectors_2_currency = "N/A"
    current.sectors_2_amount = "N/A"
    current.sectors_2_description = "N/A"
    current.sectors_3 = "N/A"
    current.sectors_3_currency = "N/A"
    current.sectors_3_amount = "N/A"
    current.sectors_3_description = "N/A"

    try:
        cleaned = str(project.sector)
        lines = re.findall("(?<=\\n)(.*?)(?=\\n)", cleaned)
        sector_descriptions = []

        for line in lines:
            if line != "":
                sector_descriptions.append(line)

        current.sectors_1 = sector_descriptions[0]
        current.sectors_1_description = re.findall(
            "(?<=- )(.+?)(?=$)", sector_descriptions[1])[0]

        if (not project.sectors == ""):
            cleaned = str(project.sectors)
            lines = re.findall("(?<=\\n)(.*?)(?=\\n)", cleaned)
            content_lines = []

            for line in lines:
                if line != "":
                    content_lines.append(line)

            current.sectors_1_currency = re.findall(
                "(?<=: )(.*?)(?= )", content_lines[1])[0]
            currency_and_amount = re.findall(
                "(?<= )(.+?)(?=$)", content_lines[1])
            current.sectors_1_amount = re.findall(
                "(?<= )(.+?)(?=$)", currency_and_amount[0])[0]

        if len(sector_descriptions) > 2:
            current.sectors_2 = sector_descriptions[2]
            current.sectors_2_description = re.findall(
                "(?<=- )(.+?)(?=$)", sector_descriptions[3])[0]
            if(not project.sectors == ""):
                current.sectors_2_currency = re.findall(
                    "(?<=: )(.*?)(?= )", content_lines[3])[0]
                currency_and_amount = re.findall(
                    "(?<= )(.+?)(?=$)", content_lines[3])
                current.sectors_2_amount = re.findall(
                    "(?<= )(.+?)(?=$)", currency_and_amount[0])[0]

        if len(sector_descriptions) > 4:
            current.sectors_3 = sector_descriptions[3]
            current.sectors_3_description = re.findall(
                "(?<=- )(.+?)(?=$)", sector_descriptions[5])[0]
            if(not project.sectors == ""):
                current.sectors_3_currency = re.findall(
                    "(?<=: )(.*?)(?= )", content_lines[5])[0]
                currency_and_amount = re.findall(
                    "(?<= )(.+?)(?=$)", content_lines[0])
                current.sectors_3_amount = re.findall(
                    "(?<= )(.+?)(?=$)", currency_and_amount[5])[0]

    except:
        except_value = "N/A"
        if project.sectors == "":
            except_value = "N/A"

        current.sectors_1 = except_value
        current.sectors_1_currency = except_value
        current.sectors_1_amount = except_value
        current.sectors_1_description = except_value
        current.sectors_2 = except_value
        current.sectors_2_currency = except_value
        current.sectors_2_amount = except_value
        current.sectors_2_description = except_value
        current.sectors_3 = except_value
        current.sectors_3_currency = except_value
        current.sectors_3_amount = except_value
        current.sectors_3_description = except_value

    current.covid_project = project.covid_project

    refactored_data.append(current)
    n += 1

statusPrint("Writing to excel")

workbook = xlsxwriter.Workbook('results.xlsx')
worksheet = workbook.add_worksheet()

worksheet.write('A1', 'link')
worksheet.write('B1', 'release_date')
worksheet.write('C1', 'status')
worksheet.write('D1', 'status_date')
worksheet.write('E1', 'reference')
worksheet.write('F1', 'project_name')
worksheet.write('G1', 'promoter')
worksheet.write('H1', 'total_cost_currency')
worksheet.write('I1', 'total_cost_amount')
worksheet.write('J1', 'total_cost_scale')
worksheet.write('K1', 'proposed_currency')
worksheet.write('L1', 'proposed_amount')
worksheet.write('M1', 'proposed_scale')
worksheet.write('N1', 'location')
worksheet.write('O1', 'description')
worksheet.write('P1', 'objectives')
worksheet.write('Q1', 'additionality_and_impact')
worksheet.write('R1', 'environmental_aspects')
worksheet.write('S1', 'procurement')
worksheet.write('T1', 'other_links')
worksheet.write('U1', 'amount_currency')
worksheet.write('V1', 'amount')
worksheet.write('W1', 'countries_1')
worksheet.write('X1', 'countries_1_currency')
worksheet.write('Y1', 'countries_1_amount')
worksheet.write('Z1', 'countries_2')
worksheet.write('AA1', 'countries_2_currency')
worksheet.write('AB1', 'countries_2_amount')
worksheet.write('AC1', 'countries_3')
worksheet.write('AD1', 'countries_3_currency')
worksheet.write('AE1', 'countries_3_amount')
worksheet.write('AF1', 'countries_4')
worksheet.write('AG1', 'countries_4_currency')
worksheet.write('AH1', 'countries_4_amount')
worksheet.write('AI1', 'countries_5')
worksheet.write('AJ1', 'countries_5_currency')
worksheet.write('AK1', 'countries_5_amount')
worksheet.write('AL1', 'countries_6')
worksheet.write('AM1', 'countries_6_currency')
worksheet.write('AN1', 'countries_6_amount')
worksheet.write('AO1', 'countries_7')
worksheet.write('AP1', 'countries_7_currency')
worksheet.write('AQ1', 'countries_7_amount')
worksheet.write('AR1', 'sectors_1')
worksheet.write('AS1', 'sectors_1_description')
worksheet.write('AT1', 'sectors_1_currency')
worksheet.write('AU1', 'sectors_1_amount')
worksheet.write('AV1', 'sectors_2')
worksheet.write('AW1', 'sectors_2_description')
worksheet.write('AX1', 'sectors_2_currency')
worksheet.write('AY1', 'sectors_2_amount')
worksheet.write('AZ1', 'sectors_3')
worksheet.write('BA1', 'sectors_3_description')
worksheet.write('BB1', 'sectors_3_currency')
worksheet.write('BC1', 'sectors_3_amount')
worksheet.write('BD1', 'covid_project')

i = 2
for project in refactored_data:

    statusPrint("Writing Project to Excel" + project.link +
                " || " + str(i - 1) + "/" + str(len(refactored_data)))

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
    worksheet.write('K'+str(i), project.proposed_currency)
    worksheet.write('L'+str(i), project.proposed_amount)
    worksheet.write('M'+str(i), project.proposed_scale)
    worksheet.write('N'+str(i), project.location)
    worksheet.write('O'+str(i), project.description)
    worksheet.write('P'+str(i), project.objectives)
    worksheet.write('Q'+str(i), project.additionality_and_impact)
    worksheet.write('R'+str(i), project.environmental_aspects)
    worksheet.write('S'+str(i), project.procurement)
    worksheet.write('T'+str(i), project.other_links)
    worksheet.write('U'+str(i), project.amount_currency)
    worksheet.write('V'+str(i), project.amount)
    worksheet.write('W'+str(i), project.countries_1)
    worksheet.write('X'+str(i), project.countries_1_currency)
    worksheet.write('Y'+str(i), project.countries_1_amount)
    worksheet.write('Z'+str(i), project.countries_2)
    worksheet.write('AA'+str(i), project.countries_2_currency)
    worksheet.write('AB'+str(i), project.countries_2_amount)
    worksheet.write('AC'+str(i), project.countries_3)
    worksheet.write('AD'+str(i), project.countries_3_currency)
    worksheet.write('AE'+str(i), project.countries_3_amount)
    worksheet.write('AF'+str(i), project.countries_4)
    worksheet.write('AG'+str(i), project.countries_4_currency)
    worksheet.write('AH'+str(i), project.countries_4_amount)
    worksheet.write('AI'+str(i), project.countries_5)
    worksheet.write('AJ'+str(i), project.countries_5_currency)
    worksheet.write('AK'+str(i), project.countries_5_amount)
    worksheet.write('AL'+str(i), project.countries_6)
    worksheet.write('AM'+str(i), project.countries_6_currency)
    worksheet.write('AN'+str(i), project.countries_6_amount)
    worksheet.write('AO'+str(i), project.countries_7)
    worksheet.write('AP'+str(i), project.countries_7_currency)
    worksheet.write('AQ'+str(i), project.countries_7_amount)
    worksheet.write('AR'+str(i), project.sectors_1)
    worksheet.write('AS'+str(i), project.sectors_1_description)
    worksheet.write('AT'+str(i), project.sectors_1_currency)
    worksheet.write('AU'+str(i), project.sectors_1_amount)
    worksheet.write('AV'+str(i), project.sectors_2)
    worksheet.write('AW'+str(i), project.sectors_2_description)
    worksheet.write('AX'+str(i), project.sectors_2_currency)
    worksheet.write('AY'+str(i), project.sectors_2_amount)
    worksheet.write('AZ'+str(i), project.sectors_3)
    worksheet.write('BA'+str(i), project.sectors_3_description)
    worksheet.write('BB'+str(i), project.sectors_3_currency)
    worksheet.write('BC'+str(i), project.sectors_3_amount)
    worksheet.write('BD'+str(i), project.covid_project)

    i += 1


workbook.close()

statusPrint("Finsihed")
