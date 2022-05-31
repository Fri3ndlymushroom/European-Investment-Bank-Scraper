import re


class Project:
    def __init__(self, index):
        self.index = index


raw_data = [
    Project(0)
]

raw_data[0].link ='https://www.eib.org/en/projects/all/20210565'
raw_data[0].release_date ='\n\n17 December 2021\n\n'
raw_data[0].status ='\n\nSigned | 11/05/2022\n\n'
raw_data[0].reference ='\n\n20210565\n\n'
raw_data[0].project_name ='\n\nWALLONIA WATER SUPPLY & CLIMATE - SWDE\n\n'
raw_data[0].promoter ='\n\nSOCIETE WALLONNE DES EAUX\n\n'
raw_data[0].total_cost ='\n\nEUR 500 million\n\n'
raw_data[0].location ='\n\n\n\nBelgium\n\n\n\n'
raw_data[0].sector ='\n\n\n\n\nWater, sewerage\n\n - Water supply; sewerage, waste management and remediation activities\n\n\n\n', 
raw_data[0].description = "\n\nUn prêt de 250 millions d'euros de la BEI à la Société Wallone des Eaux (SWDE) pour cofinancer son programme d'investissement 2022-2026 afin d'améliorer la distribution d'eau, la sécurité d'approvisionnement et de contribuer aux travaux d'adaptation liés au changement climatique.\n\n", 
raw_data[0].objectives = "\n\nLe projet concerne le programme d'investissement de la SWDE pour la période de 2022 à 2026. Il comprend la réhabilitation et la mise à niveau de tous les types de composants du système d'adduction d'eau de de la SWDE (transport, stockage, traitement et distribution). Il permettra d'améliorer l'alimentation en eau d'un bassin de près de 2,5 millions d'habitants couvrant 207 municipalités en Wallonie à travers un réseau modernisé de près de 30 000 km de longueur.\n\n", 
raw_data[0].environmental_aspects= "\n\nLes opérations de ce programme sont toutes éligibles sous la nouvelle orientation de prêts dans le secteur de l'eau de la BEI. Ce prêt devrait contribuer à corriger les défaillances du marché dans le secteur en finançant des opérations générant d'importantes externalités positives (environnement et santé publique). Par ailleurs, une part des opérations devrait contribuer à l'action climatique à la fois en terme d'atténuation et d'adaptation.\n\n"
raw_data[0].procurement ="\n\nLa Banque exigera du Promoteur d'assurer que les marchés pour la mise en œuvre du projet seront passés en conformité avec la législation applicable de l'UE (les Directives 2014/24/EC ainsi que la Directive 89/665/EEC) et la jurisprudence de la Cour européenne de justice, y compris en matière de publication des avis de passation des marchés dans le Journal officiel de l'UE tel que requis.\n\n"
raw_data[0].other_links =['https://www.eib.org/en/projects/pipelines/all/20210565', 'https://www.eib.org/en/registers/all/152481197', 'https://www.eib.org/en/press/all/2022-230-la-bei-et-la-societe-wallonne-des-eaux-signent-un-pret-de-250-millions-d-eur-pour-des-investissements-au-service-de-la-resilience-climatique']
raw_data[0].other_links_title =['WALLONIA WATER SUPPLY & CLIMATE - SWDE', 'Environmental and Social Data Sheet (ESDS) - WALLONIA WATER SUPPLY & CLIMATE - SWDE', 'Belgium: EIB and Société wallonne des eaux sign €250 million loan for climate resilience investment']
raw_data[0].amount ='\n\n€ 250,000,000\n\n'
raw_data[0].countries ='\n\nBelgium\n: € 250,000,000\n\n'
raw_data[0].sectors ='\n\nEnergy\n: € 3,000,000\n\n\nIndustry\n: € 27,000,000\n\n'
raw_data[0].covid_project = False


class Refactored:
    def __init__(self):
        0


# refactor
for project in raw_data:
    
    current = Refactored()

    # index
    current.index = project.index

    # link
    current.link = project.link

    # release date
    current.release_date = project.release_date.strip()

    #status
    cleaned = project.status.strip()
    current.status = re.search("(.*?)(?= \|)", cleaned)[0]
    current.status_date = re.search("(?<=\| ).*$", cleaned)[0]

    #reference
    current.reference = project.reference.strip()

    #project name
    current.project_name = project.project_name.strip()
    #promoter
    current.promoter = project.promoter.strip()

    #total cost
    cleaned = project.total_cost.strip()
    parts = re.findall("[^ ]*", cleaned)
    current.total_cost_currency = parts[0]
    current.total_cost_amount = parts[2]
    current.total_cost_scale = parts[4]

    #location
    current.location = project.location.strip()

    #sector
    cleaned = project.sector[0].replace("\n", "")
    current.sector = re.search("^(.*?)(?= -)", cleaned)[0]
    current.sector_description = re.search("(?<=- ).*$", cleaned)[0]

    # description
    current.description = project.description[0].strip()

    # objectives
    current.objectives = project.objectives[0].strip()

    # environmental aspects
    current.environmental_aspects = project.environmental_aspects.strip()

    #procurement
    current.procurement = project.procurement.strip()

    # other links
    linkstring = ""

    i = 0
    for link in project.other_links:
        linkstring = linkstring + project.other_links_title[i] + ": " + link + " || "
        i+= 1

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
    current.countries_1_currency = re.findall("(?<=: )(.*?)(?= )", content_lines[1])[0]
    currency_and_amount = re.findall("(?<= )(.+?)(?=$)", content_lines[1])
    current.countries_1_amount = re.findall("(?<= )(.+?)(?=$)", currency_and_amount[0])[0]

    if len(content_lines) > 2:
        current.countries_2 = content_lines[2]
        current.countries_2_currency = re.findall("(?<=: )(.*?)(?= )", content_lines[3])[0]
        currency_and_amount = re.findall("(?<= )(.+?)(?=$)", content_lines[3])
        current.countries_2_amount = re.findall("(?<= )(.+?)(?=$)", currency_and_amount[0])[0]
    else: 
        current.countries_2 = ""
        current.countries_2_currency = ""
        current.countries_2_amount = ""
    
    if len(content_lines) > 4:
        current.countries_3 = content_lines[4]
        current.countries_3_currency = re.findall("(?<=: )(.*?)(?= )", content_lines[5])[0]
        currency_and_amount = re.findall("(?<= )(.+?)(?=$)", content_lines[5])
        current.countries_3_amount = re.findall("(?<= )(.+?)(?=$)", currency_and_amount[0])[0]
    else: 
        current.countries_3 = ""
        current.countries_3_currency = ""
        current.countries_3_amount = ""
 

    # sectors
    cleaned = str(project.sectors)
    lines = re.findall("(?<=\\n)(.*?)(?=\\n)", cleaned)
    content_lines = []
    
    for line in lines:
        if line != "":
            content_lines.append(line)

    current.sectors_1 = content_lines[0]
    current.sectors_1_currency = re.findall("(?<=: )(.*?)(?= )", content_lines[1])[0]
    currency_and_amount = re.findall("(?<= )(.+?)(?=$)", content_lines[1])
    current.sectors_1_amount = re.findall("(?<= )(.+?)(?=$)", currency_and_amount[0])[0]

    if len(content_lines) > 2:
        current.sectors_2 = content_lines[2]
        current.sectors_2_currency = re.findall("(?<=: )(.*?)(?= )", content_lines[3])[0]
        currency_and_amount = re.findall("(?<= )(.+?)(?=$)", content_lines[3])
        current.sectors_2_amount = re.findall("(?<= )(.+?)(?=$)", currency_and_amount[0])[0]
    else: 
        current.sectors_2 = ""
        current.sectors_2_currency = ""
        current.sectors_2_amount = ""
    
    if len(content_lines) > 4:
        current.sectors_3 = content_lines[4]
        current.sectors_3_currency = re.findall("(?<=: )(.*?)(?= )", content_lines[5])[0]
        currency_and_amount = re.findall("(?<= )(.+?)(?=$)", content_lines[5])
        current.sectors_3_amount = re.findall("(?<= )(.+?)(?=$)", currency_and_amount[0])[0]
    else: 
        current.sectors_3 = ""
        current.sectors_3_currency = ""
        current.sectors_3_amount = ""

    print(current.__dict__)








