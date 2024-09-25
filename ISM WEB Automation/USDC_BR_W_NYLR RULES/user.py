import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id_general = 'USDC_BR_W_NYLR RULES'
location_id_general = 'General And Standing Orders'

source_id_administrative = 'USDC_BR_W_NYLR RULES'
location_id_administrative = 'Administrative Procedures and Orders'

source_id_local = 'USDC_BR_W_NYLR RULES'
location_id_local = 'Local Rules'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'General And Standing Orders': 'https://www.nywb.uscourts.gov/general-and-standingorders',
    'Administrative Procedures and Orders': 'https://www.nywb.uscourts.gov/administrative-procedures-and-orders',
    'Western District of New York Local Bankruptcy Rules': 'https://www.nywb.uscourts.gov/court-info/local-rules-and-orders',
}

def rule_check_pdf(rule_name, pdf_content, file_name, source_id, location_id):
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

def format_pdf_name_general(pdf_name):
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"  # Removed ".pdf" part

def format_pdf_name_administrative(li_element):
    return li_element.get_text(strip=True)

def format_pdf_name(pdf_name):
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"  # Removed ".pdf" part

for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    div_content = soup.find('div', class_='field__items')

    if category == 'General And Standing Orders':
        if div_content:
            links = div_content.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if '/sites/nywb/files/' in href:
                    pdf_url = urllib.parse.urljoin(url, href)
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        pdf_name = link.get_text(strip=True)
                        output_file_name = format_pdf_name_general(pdf_name)
                        rule_check_pdf(pdf_name, response.content, output_file_name, source_id_general, location_id_general)
                    else:
                        print(f"Failed to download: {pdf_url}")

    elif category == 'Administrative Procedures and Orders':
        if div_content:
            li_elements = div_content.find_all('li')
            for li_element in li_elements:
                link = li_element.find('a', href=True)
                if link and '/sites/nywb/files/' in link.get('href'):
                    pdf_url = urllib.parse.urljoin(url, link.get('href'))
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        pdf_name = format_pdf_name_administrative(li_element)
                        output_file_name = format_pdf_name_administrative(li_element)
                        rule_check_pdf(pdf_name, response.content, output_file_name, source_id_administrative, location_id_administrative)
                    else:
                        print(f"Failed to download: {pdf_url}")

    elif category == 'Western District of New York Local Bankruptcy Rules':
        if div_content:
            links = div_content.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if '/sites/nywb/files/' in href:
                    pdf_url = urllib.parse.urljoin(url, href)
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        pdf_name = link.get_text(strip=True)
                        output_file_name = format_pdf_name(pdf_name)
                        rule_check_pdf(pdf_name, response.content, output_file_name, source_id_local, location_id_local)
                    else:
                        print(f"Failed to download: {pdf_url}")
