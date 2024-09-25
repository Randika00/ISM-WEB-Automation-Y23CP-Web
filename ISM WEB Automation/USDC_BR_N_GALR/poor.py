import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id = 'USDC_BR_N_GALR RULES'
location_id = 'General Orders'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'Northern District of Georgia Local Bankruptcy Rules - 01': 'https://www.ganb.uscourts.gov/court-info/local-rules-and-orders/general-orders',
}


# Function to check PDF rules
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

# Function to format PDF names
def format_pdf_name(pdf_name):
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"


for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    ul_elements = soup.find_all('ul')

    for ul_element in ul_elements:
        links = ul_element.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            if "/content/" in href:
                # You can add additional filtering conditions here if needed
                print(f"Link with /content/: {href}")







