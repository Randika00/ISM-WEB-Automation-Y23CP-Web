import requests
import os
from bs4 import BeautifulSoup
import common_module
import re

source_id = 'US_Courts_FIRSTBAPLR'
location_id = 'General Rules'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'BAP Local Rules': 'http://www.bap1.uscourts.gov/rules-procedures',
    'Quick Reference Guide': 'http://www.bap1.uscourts.gov/rules-procedures',
    'Practice Guide': 'http://www.bap1.uscourts.gov/rules-procedures'
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

    ul_Content = soup.find('ul', class_='menu')
    li_element = ul_Content.findAll('li')

    if rule_name == 'BAP Local Rules':
        pdf_url = 'https://www.bap1.uscourts.gov/sites/bap1/files/BAP%20Local%20Rules.pdf'
    elif rule_name == 'Quick Reference Guide':
        pdf_url = 'https://www.bap1.uscourts.gov/sites/bap1/files/BAP_QuickReference.pdf'
    elif rule_name == 'Practice Guide':
        pdf_url = 'https://www.bap1.uscourts.gov/sites/bap1/files/BAP_Guide.pdf'

    print(pdf_url)
    pdf_response = requests.get(pdf_url)
    output_fileName = common_module.ret_file_name_full(source_id, location_id, rule_name, '.pdf')
    with open(output_fileName, 'wb') as pdf_file:
        pdf_file.write(pdf_response.content)
    print(f"Downloaded: {output_fileName}")
