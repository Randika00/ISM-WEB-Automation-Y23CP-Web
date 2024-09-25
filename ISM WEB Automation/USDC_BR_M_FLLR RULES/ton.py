import requests
from bs4 import BeautifulSoup
import common_module
import re

source_id = 'USDC_BR_M_FLLR RULES'
location_id = 'Local Rules'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'Middle District of Florida Local Bankruptcy Rules': 'http://www.flmb.uscourts.gov/localrules/',
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

def format_pdf_name(pdf_name):
    # Replace '.' and ';' with ' ' and then insert '.' after the first sequence of digits
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"  # Removed ".pdf" part

for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    p_elements = soup.find_all('p')
    pdf_url = 'http://www.flmb.uscourts.gov/localrules/Rules/localrules-FLMB.pdf?id=3'
    print(pdf_url)
    pdf_response = requests.get(pdf_url)
    pdf_name = "Local Rules effective August 1, 2023"  # Set the desired PDF name
    output_file_name = common_module.ret_file_name_full(source_id, location_id, format_pdf_name(pdf_name), '.pdf')
    with open(output_file_name, 'wb') as pdf_file:
        pdf_file.write(pdf_response.content)
    print(f"Downloaded: {output_file_name}")
