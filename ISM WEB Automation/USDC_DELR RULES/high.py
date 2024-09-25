import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse
import os
from datetime import datetime

source_id = 'USDC_DELR RULES'
allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')


# Define functions for rule checking and formatting PDF names for Standing Orders
def rule_check_pdf_standing_orders(rule_name, pdf_content, file_name, location_id):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)

    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id, cleaned_rule_title_new)

        today_date = datetime.today().strftime('%Y%m%d')
        output_directory = os.path.join('out', source_id, today_date, location_id)
        os.makedirs(output_directory, exist_ok=True)
        output_file_name = os.path.join(output_directory, format_pdf_name(file_name))

        with open(output_file_name, 'wb') as file:
            file.write(pdf_content)
            print(f"Downloaded Standing Orders: {output_file_name}")


# Define functions for rule checking and formatting PDF names for Local Rules
def rule_check_pdf_local_rules(rule_name, pdf_content, file_name, location_id):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)

    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id, cleaned_rule_title_new)

        today_date = datetime.today().strftime('%Y%m%d')
        output_directory = os.path.join('out', source_id, today_date, location_id)
        os.makedirs(output_directory, exist_ok=True)
        output_file_name = os.path.join(output_directory, format_pdf_name(file_name))

        with open(output_file_name, 'wb') as file:
            file.write(pdf_content)
            print(f"Downloaded Local Rules: {output_file_name}")


# Processing for Standing Orders
def process_standing_orders(url):
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    tr_elements = soup.find_all('tr')

    for tr_element in tr_elements:
        try:
            links = tr_element.find_all('a', href=True)
            for link in links:
                href = link['href']
                if '/sites/ded/files/general-orders/' in href:
                    pdf_url = urllib.parse.urljoin(url, href)
                    print(f"Downloading Standing Orders: {pdf_url}")
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        pdf_name = link.get_text(strip=True)
                        output_file_name = format_pdf_name(pdf_name)
                        rule_check_pdf_standing_orders(pdf_name, response.content, output_file_name, 'Standing Orders')
                    else:
                        print(f"Failed to download Standing Orders: {pdf_url} - Status Code: {response.status_code}")
        except Exception as e:
            print(f"Exception occurred: {str(e)}")


# Processing for Local Rules
def process_local_rules(url):
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    div_content = soup.find('div', class_='field__items')

    if div_content:
        links = div_content.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            if '/sites/ded/files/local-rules/' in href:
                pdf_url = urllib.parse.urljoin(url, href)
                response = requests.get(pdf_url)
                if response.status_code == 200:
                    pdf_name = link.get_text(strip=True)
                    output_file_name = format_pdf_name(pdf_name)
                    rule_check_pdf_local_rules(pdf_name, response.content, output_file_name, 'Local Rules')
                else:
                    print(f"Failed to download Local Rules: {pdf_url}")


# Function to format PDF names
def format_pdf_name(pdf_name):
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}.pdf"


# URLs for Standing Orders and Local Rules
sheet_links = {
    'District of Delaware Standing Orders': 'https://www.ded.uscourts.gov/court-info/local-rules-and-orders/general-orders',
    'District of Delaware Local Rules': 'https://www.ded.uscourts.gov/local-rules',
}

# Processing for Standing Orders and Local Rules
for category, url in sheet_links.items():
    if 'Standing Orders' in category:
        process_standing_orders(url)
    elif 'Local Rules' in category:
        process_local_rules(url)
