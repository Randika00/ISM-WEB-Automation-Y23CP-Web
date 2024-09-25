import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse
import os
import sys
from datetime import datetime

source_id = 'USDC_BR_W_WILR RULES'
location_id_local = 'Local Rules'
location_id_general = 'General Orders'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

def rule_check_pdf(rule_name, pdf_content, file_name):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)

    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id, cleaned_rule_title_new)

        output_file_name = common_module.ret_file_name_full(source_id, location_id_general, file_name, '.pdf')
        with open(output_file_name, 'wb') as file:
            file.write(pdf_content)
            print(f"Downloaded: {output_file_name}")

def format_pdf_name(pdf_name):
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"

def rule_check_html(rule_name, html_content):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)
    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id, cleaned_rule_title_new)
        output_file_name = common_module.ret_file_name_full(source_id, location_id_local, cleaned_rule_title_new, '.html')
        with open(output_file_name, 'w', encoding='utf-8') as file:
            file.write(str(html_content))
            print(f"Downloaded HTML: {output_file_name}")

sheet_links = {
    'Western District of Wisconsin General Orders': 'https://www.wiwb.uscourts.gov/general-orders',
    'Western District of Wisconsin Local Bankruptcy Rules': 'https://www.wiwb.uscourts.gov/court-info/local-rules-and-orders'
}

for location_id, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    if 'general-orders' in url:
        tr_elements = soup.find_all('tr')
        for tr_element in tr_elements:
            try:
                links = tr_element.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if '/sites/wiwb/files/' in href:
                        pdf_url = urllib.parse.urljoin(url, href)
                        print(f"Downloading PDF: {pdf_url}")
                        response = requests.get(pdf_url)
                        if response.status_code == 200:
                            pdf_name = link.get_text(strip=True)
                            output_file_name = format_pdf_name(pdf_name)
                            rule_check_pdf(pdf_name, response.content, output_file_name)
                        else:
                            print(f"Failed to download PDF: {pdf_url} - Status Code: {response.status_code}")
            except Exception as e:
                print(f"Exception occurred: {str(e)}")
    else:
        div_content = soup.find('div', class_='field__items')
        if div_content:
            html_content = str(div_content)
            file_extension = '.html'
            out_folder = common_module.ret_out_folder(source_id, location_id)
            file_name = common_module.ret_file_name_full(source_id, location_id_local, location_id, file_extension)
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(html_content)
            print(f"Downloaded HTML content for '{location_id}' to {file_name}")
        else:
            print(f"Unable to find the content for '{location_id}'")
