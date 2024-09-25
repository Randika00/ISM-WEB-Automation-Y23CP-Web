import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id = 'USDC_BR_N_NYLR RULES'

# First Section - Administrative Orders
location_id_admin_orders = 'Administrative Orders'
allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links_admin_orders = {
    'Northern District of New York Local Bankruptcy Rules': 'https://www.nynb.uscourts.gov/administrative-orders',
}

def rule_check_pdf(rule_name, pdf_content, file_name):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)

    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id, cleaned_rule_title_new)

        output_file_name = common_module.ret_file_name_full(source_id, location_id_admin_orders, file_name, '.pdf')
        with open(output_file_name, 'wb') as file:
            file.write(pdf_content)
            print(f"Downloaded: {output_file_name}")

def format_pdf_name(pdf_name):
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"

for category, url in sheet_links_admin_orders.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    div_content = soup.find('div', class_='view-content')
    if div_content:
        links = div_content.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            if 'sites/nynb/files/AdminOrders/' in href:
                pdf_url = urllib.parse.urljoin(url, href)
                response = requests.get(pdf_url)
                if response.status_code == 200:
                    pdf_name = link.get_text(strip=True)
                    output_file_name = format_pdf_name(pdf_name)
                    rule_check_pdf(pdf_name, response.content, output_file_name)
                else:
                    print(f"Failed to download: {pdf_url}")

# Second Section - Local Rules
location_id_local_rules = 'Local Rules'
sheet_links_local_rules = {
    'Northern District of New York Local Bankruptcy Rules': 'https://www.nynb.uscourts.gov/local-rules-general-orders',
}

for category, url in sheet_links_local_rules.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    ul_elements = soup.find_all('ul')
    pdf_url = 'https://www.nynb.uscourts.gov/sites/nynb/files/LBR_GenOrders/Local%20Bankruptcy%20Rules_Effective%2012-01-2023%20Final.pdf'
    print(pdf_url)
    pdf_response = requests.get(pdf_url)
    pdf_name = "Local Bankruptcy Rules"
    output_file_name = common_module.ret_file_name_full(source_id, location_id_local_rules, format_pdf_name(pdf_name), '.pdf')
    with open(output_file_name, 'wb') as pdf_file:
        pdf_file.write(pdf_response.content)
    print(f"Downloaded: {output_file_name}")
