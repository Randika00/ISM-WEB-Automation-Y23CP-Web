import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id = 'USDC_C_ILLR RULES'
location_id_general_standing_orders = 'General and Standing Orders'
location_id_local_rules = 'Local Rules'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

general_standing_orders_link = {
    'Central District of Illinois General and Standing Orders': 'https://www.ilcd.uscourts.gov/general-and-standing-orders',
}

local_rules_link = {
    'Central District of Illinois Local Rules': 'https://www.ilcd.uscourts.gov/local-rules',
}

def rule_check_pdf(source_id, location_id, rule_name, pdf_content, file_name):
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
    return f"{formatted_name.strip()}"

# Process General and Standing Orders
for category, url in general_standing_orders_link.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    tr_elements = soup.find_all('tr')

    for tr_element in tr_elements:
        try:
            links = tr_element.find_all('a', href=True)
            for link in links:
                href = link['href']
                if '/sites/ilcd/files/' in href:
                    pdf_url = urllib.parse.urljoin(url, href)
                    print(f"Downloading: {pdf_url}")
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        pdf_name = link.get_text(strip=True)
                        output_file_name = format_pdf_name(pdf_name)
                        rule_check_pdf(source_id, location_id_general_standing_orders, pdf_name, response.content, output_file_name)
                    else:
                        print(f"Failed to download: {pdf_url} - Status Code: {response.status_code}")
        except Exception as e:
            print(f"Exception occurred: {str(e)}")

# Process Local Rules
for category, url in local_rules_link.items():
    pdf_url = 'https://www.ilcd.uscourts.gov/sites/ilcd/files/August%2011%202023%20Local%20Rules.pdf'
    print(f"Downloading: {pdf_url}")
    pdf_response = requests.get(pdf_url)
    pdf_name = "Local Rules - Effective August 11, 2023 "  # Set the desired PDF name
    output_file_name = common_module.ret_file_name_full(source_id, location_id_local_rules, format_pdf_name(pdf_name), '.pdf')
    with open(output_file_name, 'wb') as pdf_file:
        pdf_file.write(pdf_response.content)
    print(f"Downloaded: {output_file_name}")
