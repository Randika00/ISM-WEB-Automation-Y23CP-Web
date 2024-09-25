import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id_local_rules = 'USDC_BR_W_MILR RULES'
location_id_local_rules = 'Local Rules'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

# Handling Local Rules
sheet_links_local_rules = {
    'Western District of Michigan Local Bankruptcy Rules': 'https://www.miwb.uscourts.gov/court-info/local-rules-and-orders/local-rules',
}

def rule_check_pdf_local_rules(rule_name, pdf_content, file_name):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)

    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id_local_rules, cleaned_rule_title_new)

        output_file_name = common_module.ret_file_name_full(source_id_local_rules, location_id_local_rules, file_name, '.pdf')
        with open(output_file_name, 'wb') as file:
            file.write(pdf_content)
            print(f"Downloaded: {output_file_name}")

def format_pdf_name(pdf_name):
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"

for category, url in sheet_links_local_rules.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    div_content = soup.find('div', class_='view-content')
    if div_content:
        links = div_content.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            if 'https://www.miwb.uscourts.gov/sites/miwb/files/local_rules/Local%20Rules%20Bookmarked_1.1.23%20%28003%29.pdf' in href:
                pdf_url = urllib.parse.urljoin(url, href)
                response = requests.get(pdf_url)
                if response.status_code == 200:
                    pdf_name = link.get_text(strip=True)
                    output_file_name = format_pdf_name(pdf_name)
                    rule_check_pdf_local_rules(pdf_name, response.content, output_file_name)
                else:
                    print(f"Failed to download: {pdf_url}")

source_id_admin_orders = 'USDC_BR_W_MILR RULES'
location_id_admin_orders = 'Administrative Orders'

# Handling Administrative Orders
sheet_links_admin_orders = {
    'Western District of Michigan Administrative Orders 01': 'https://www.miwb.uscourts.gov/court-info/local-rules-and-orders/general-orders',
    'Western District of Michigan Administrative Orders 02': 'https://www.miwb.uscourts.gov/court-info/local-rules-and-orders/general-orders?page=1',
    'Western District of Michigan Administrative Orders 03': 'https://www.miwb.uscourts.gov/court-info/local-rules-and-orders/general-orders?page=2',
    'Western District of Michigan Administrative Orders 04': 'https://www.miwb.uscourts.gov/court-info/local-rules-and-orders/general-orders?page=3',
    'Western District of Michigan Administrative Orders 05': 'https://www.miwb.uscourts.gov/court-info/local-rules-and-orders/general-orders?page=4',
    'Western District of Michigan Administrative Orders 06': 'https://www.miwb.uscourts.gov/court-info/local-rules-and-orders/general-orders?page=5',
    'Western District of Michigan Administrative Orders 07': 'https://www.miwb.uscourts.gov/court-info/local-rules-and-orders/general-orders?page=6',
    'Western District of Michigan Administrative Orders 08': 'https://www.miwb.uscourts.gov/court-info/local-rules-and-orders/general-orders?page=7',
    'Western District of Michigan Administrative Orders 09': 'https://www.miwb.uscourts.gov/court-info/local-rules-and-orders/general-orders?page=8',

}

def rule_check_pdf_admin_orders(rule_name, pdf_content, file_name):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)

    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id_admin_orders, cleaned_rule_title_new)

        output_file_name = common_module.ret_file_name_full(source_id_admin_orders, location_id_admin_orders, file_name, '.pdf')
        with open(output_file_name, 'wb') as file:
            file.write(pdf_content)
            print(f"Downloaded: {output_file_name}")

for category, url in sheet_links_admin_orders.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    div_content = soup.find('div', class_='view-content')
    if div_content:
        links = div_content.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            if 'https://www.miwb.uscourts.gov/sites/miwb/files/general-ordes/' in href:
                pdf_url = urllib.parse.urljoin(url, href)
                response = requests.get(pdf_url)
                if response.status_code == 200:
                    pdf_name = link.get_text(strip=True)
                    output_file_name = format_pdf_name(pdf_name)
                    rule_check_pdf_admin_orders(pdf_name, response.content, output_file_name)
                else:
                    print(f"Failed to download: {pdf_url}")
