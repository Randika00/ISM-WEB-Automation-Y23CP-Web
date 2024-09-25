import requests
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys
import common_module

source_id = 'US_Courts_SIXTHBAPLR_Rules'
location_id = 'Forms'

allowed_rules = []
ignore_rules = []

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'Pro Se BAP Brief Form': 'https://www.ca6.uscourts.gov/bankruptcy-appellate-panel'
}

def rule_check_pdf(rule_name, pdf_content, file_name):
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

    div_content = soup.find('div', class_='view-content')
    li_element = div_content.findAll('li')
    pdf_url = 'https://www.ca6.uscourts.gov/sites/ca6/files/documents/bap/bap_brief2.pdf'
    print(pdf_url)
    pdf_response = requests.get(pdf_url)
    output_fileName = common_module.ret_file_name_full(source_id, location_id, rule_name, '.pdf')
    with open(output_fileName, 'wb') as pdf_file:
        pdf_file.write(pdf_response.content)
    print(f"Downloaded: {output_fileName}")
