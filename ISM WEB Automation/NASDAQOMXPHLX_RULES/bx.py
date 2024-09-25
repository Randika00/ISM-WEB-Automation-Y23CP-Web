import os
import requests
from bs4 import BeautifulSoup
import common_module
import re

source_id = 'NASDAQOMXPHLX_RULE'
location_id = 'Corporate Rules'

allowed_rules = []
ignore_rules = []

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'General': 'https://listingcenter.nasdaq.com/rulebook/phlx/rules',
}

def sanitize_rule_name(rule_name):
    # Remove invalid characters from the rule name
    return re.sub(r'[\/:*?"<>|]', '_', rule_name)

def get_file_name_from_href(href):
    # Extract file name from the href attribute
    return href.split('/')[-1]

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
    try:
        resource = requests.get(url)
        resource.raise_for_status()
        soup = BeautifulSoup(resource.text, "html.parser")

        pdf_folder = 'out'
        os.makedirs(pdf_folder, exist_ok=True)

        td_content = soup.find('td', class_='rules-sub-block corp')
        ul_element = td_content.findAll('ul')

        for item in ul_element:
            li_element = item.findAll('li')
            for li in li_element:
                if li.find('a'):
                    pdf_url = 'https://listingcenter.nasdaq.com/' + str(li.find('a')['href'])
                    pdf_response = requests.get(pdf_url, stream=True)

                    if pdf_response.status_code == 200:
                        file_name = get_file_name_from_href(li.find('a')['href'])
                        rule_check(rule_name, pdf_response.content, file_name)

    except requests.RequestException as e:
        print(f"Error: {e}")













