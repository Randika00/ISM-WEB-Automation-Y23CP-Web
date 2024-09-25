import os
import requests
from bs4 import BeautifulSoup
import common_module
import re

source_id = 'USDC_BR_EW_ARLR'

# General Rules
location_id_general = 'General Rules'
allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')
sheet_links_general = {
    'Local Rules': 'https://www.arb.uscourts.gov/general-orders',
}

# Administrative Rules
location_id_administrative = 'Administrative Rules'
sheet_links_administrative = {
    'Local Rules': 'https://www.arb.uscourts.gov/administrative-orders',
}

# Local Rules
location_id_local = 'Local Rules'
sheet_links_local = {
    'Local Rules': 'https://www.arb.uscourts.gov/local-rules',
}

def rule_check_pdf(rule_name, pdf_content, file_name, location_id):
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

def get_valid_filename(s):
    return "".join([c for c in s if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()

# Process General Rules
for category, url in sheet_links_general.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    td_elements = soup.find_all("td")
    for td_element in td_elements:
        link = td_element.find('a')
        if link and link['href'].endswith('.pdf'):
            pdf_url = 'https://www.arb.uscourts.gov/' + link['href']
            pdf_response = requests.get(pdf_url, stream=True)

            if pdf_response.status_code == 200:
                filename_from_href = link.text.strip()
                valid_filename = get_valid_filename(filename_from_href)
                file_ext = os.path.splitext(pdf_url)[1]
                file_name = f"{valid_filename}{file_ext}"
                rule_check_pdf(category, pdf_response.content, file_name, location_id_general)
                print(f"Downloaded: {file_name}")
            else:
                print(f"Failed to download: {pdf_url}")

# Process Administrative Rules
for category, url in sheet_links_administrative.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    p_elements = soup.find_all("p")
    for p_element in p_elements:
        link = p_element.find('a')
        if link and link['href'].endswith('.pdf'):
            pdf_url = 'https://www.arb.uscourts.gov/' + link['href']
            pdf_response = requests.get(pdf_url, stream=True)

            if pdf_response.status_code == 200:
                filename_from_href = link.text.strip()
                valid_filename = get_valid_filename(filename_from_href)
                file_ext = os.path.splitext(pdf_url)[1]
                file_name = f"{valid_filename}{file_ext}"
                rule_check_pdf(category, pdf_response.content, file_name, location_id_administrative)
                print(f"Downloaded: {file_name}")
            else:
                print(f"Failed to download: {pdf_url}")

# Process Local Rules
for category, url in sheet_links_local.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    ul_elements = soup.find_all('ul')

    for ul_element in ul_elements:
        li_elements = ul_element.find_all('li')

        for li in li_elements:
            link = li.find('a')

            if link and link['href'].endswith('.pdf'):
                pdf_url = 'https://www.arb.uscourts.gov/' + link['href']
                pdf_response = requests.get(pdf_url, stream=True)

                if pdf_response.status_code == 200:
                    filename_from_href = link.text.strip()
                    valid_filename = get_valid_filename(filename_from_href)
                    file_ext = os.path.splitext(pdf_url)[1]
                    file_name = f"{valid_filename}{file_ext}"
                    rule_check_pdf(category, pdf_response.content, file_name, location_id_local)
                    print(f"Downloaded: {file_name}")
                else:
                    print(f"Failed to download: {pdf_url}")
