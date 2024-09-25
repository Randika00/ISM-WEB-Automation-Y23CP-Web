import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id_general = 'USDC_BR_W_OKLR RULES'
location_id_general = 'General Orders'

source_id_local = 'USDC_BR_W_OKLR RULES'
location_id_local = 'Local Rules'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'Western District of Oklahoma General Orders': 'https://www.okwb.uscourts.gov/general-orders',
    'Western District of Oklahoma Local Bankruptcy Rules': 'https://www.okwb.uscourts.gov/court-info/local-rules-and-orders',
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
    return f"{formatted_name.strip()}"

def format_pdf_name_local(pdf_name):
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"

for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    if category == 'Western District of Oklahoma General Orders':
        tr_elements = soup.find_all('tr')
        for tr_element in tr_elements:
            links = tr_element.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if '/sites/okwb/files/' in href:
                    pdf_url = urllib.parse.urljoin(url, href)
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        pdf_name = link.get_text(strip=True)
                        output_file_name = format_pdf_name_general(pdf_name)
                        rule_check_pdf(pdf_name, response.content, output_file_name, source_id_general, location_id_general)
                    else:
                        print(f"Failed to download: {pdf_url}")

    elif category == 'Western District of Oklahoma Local Bankruptcy Rules':
        div_content = soup.find('div', class_='field__items')
        if div_content:
            links = div_content.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if '/okwb/files/Local_Rules.pdf' in href:
                    pdf_url = urllib.parse.urljoin(url, href)
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        pdf_name = link.get_text(strip=True)
                        output_file_name = format_pdf_name_local(pdf_name)
                        rule_check_pdf(pdf_name, response.content, output_file_name, source_id_local, location_id_local)
                    else:
                        print(f"Failed to download: {pdf_url}")
