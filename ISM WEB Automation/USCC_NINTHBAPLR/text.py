import os
import requests
from bs4 import BeautifulSoup
import common_module
import re
from datetime import datetime

source_id = 'USCC_NINTHBAPLR'
location_id = 'Local Rules'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'Circuit Rules': 'https://www.ca9.uscourts.gov/rules/',
    'NINTH CIRCUIT GENERAL': 'https://www.ca9.uscourts.gov/rules/general-orders/',
    'Local Rules File': 'https://www.ca9.uscourts.gov/bap/',
    'Local Rules File 1': 'https://www.ca9.uscourts.gov/rules/administrative-orders/',
    'Local Rules File 2': 'https://www.ca9.uscourts.gov/rules/proposed-rules-and-amendments/',
}

def rule_check(rule_name, pdf_content, file_name):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)

    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id, cleaned_rule_title_new)

        output_file_name = common_module.ret_file_name_full(source_id, location_id, file_name, '.pdf')
        with open(output_file_name, 'wb') as file:
            file.write(pdf_content)
            print(f"Downloaded: {output_file_name}")

def save_pdf(pdf_url, file_name):
    try:
        response = requests.get(pdf_url)
        if response.status_code == 200:
            # Get today's date to create the subfolder name
            today_date = datetime.now().strftime("%Y%m%d")
            output_folder = os.path.join('out', source_id, today_date, location_id)
            os.makedirs(output_folder, exist_ok=True)

            output_file_name = os.path.join(output_folder, file_name)
            with open(output_file_name, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded: {output_file_name}")
        else:
            print(f"Failed to fetch PDF from {pdf_url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading PDF from {pdf_url}: {e}")

for rule_name, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    pdf_folder = 'out'
    os.makedirs(pdf_folder, exist_ok=True)
    error_dict = {}
    error_list = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    div_Content = soup.find('div', class_='contentBody')

    if 'Circuit Rules' in rule_name:
        pdf_url = 'https://cdn.ca9.uscourts.gov/datastore/uploads/rules/frap.pdf'
        pdf_response = requests.get(pdf_url)
        output_fileName = common_module.ret_file_name_full(source_id, location_id, rule_name, '.pdf')
        with open(output_fileName, 'wb') as pdf_file:
            pdf_file.write(pdf_response.content)
        print(f"Downloaded: {output_fileName}")

    elif 'NINTH CIRCUIT GENERAL' in rule_name:
        pdf_url = 'https://cdn.ca9.uscourts.gov/datastore/uploads/rules/general_orders/General Orders.pdf'
        pdf_response = requests.get(pdf_url)
        output_fileName = common_module.ret_file_name_full(source_id, location_id, rule_name, '.pdf')
        with open(output_fileName, 'wb') as pdf_file:
            pdf_file.write(pdf_response.content)
        print(f"Downloaded: {output_fileName}")

    elif 'Local Rules File' in rule_name:
        div_Content = soup.find('div', class_='informationBox')
        pdf_url = 'https://cdn.ca9.uscourts.gov/datastore/bap/2015/06/18/baprules.pdf'
        pdf_response = requests.get(pdf_url)
        output_fileName = common_module.ret_file_name_full(source_id, location_id, rule_name, '.pdf')
        with open(output_fileName, 'wb') as pdf_file:
            pdf_file.write(pdf_response.content)
        print(f"Downloaded: {output_fileName}")

    div_Content = soup.find('div', class_='contentBody')
    pdf_urls = []

    for li in div_Content.find_all('a'):
        if li.get('href').endswith('.pdf'):
            pdf_url = li.get('href')
            pdf_urls.append(pdf_url)

    for pdf_url in pdf_urls:
        file_name = os.path.basename(pdf_url)
        print(f"Downloading {file_name} from {pdf_url}")
        save_pdf(pdf_url, file_name)
