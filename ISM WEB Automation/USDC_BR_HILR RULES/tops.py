import os
import requests
from bs4 import BeautifulSoup
import common_module
import re
from urllib.parse import urljoin, unquote

source_id = 'USDC_BR_HILR RULES'
location_id = 'Local Bankruptcy Rules'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'Local Rules and General Orders': 'https://www.hib.uscourts.gov/local-rules-and-general-orders',
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

def get_valid_filename(s):
    return "".join([c for c in s if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()


for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    h3_elements = soup.findAll('h3')

    for h3_element in h3_elements:
        strong_elements = h3_element.find_all('strong')

        for li in strong_elements:
            link = li.find('a')

            if link and link['href'].endswith('.pdf'):
                pdf_url = 'https://www.hib.uscourts.gov/' + link['href']
                pdf_response = requests.get(pdf_url, stream=True)

                if pdf_response.status_code == 200:
                    filename_from_href = link.text.strip()
                    valid_filename = get_valid_filename(filename_from_href)
                    file_ext = os.path.splitext(pdf_url)[1]
                    file_name = f"{valid_filename}{file_ext}"
                    rule_check_pdf(category, pdf_response.content, file_name)
                    print(f"Downloaded: {file_name}")
                else:
                    print(f"Failed to download: {pdf_url}")

source_id = 'USDC_BR_HILR RULES'
location_id = 'General Orders Rules'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'Local Rules and General Orders': 'https://www.hib.uscourts.gov/general-orders',
}

for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    base_url = 'https://www.hib.uscourts.gov/'
    pdf_links = [(urljoin(base_url, unquote(link['href'])), link.text) for link in soup.find_all('a', href=True) if link['href'].endswith('.pdf')]

    for pdf_url, pdf_name in pdf_links:
        pdf_response = requests.get(pdf_url, stream=True)

        if pdf_response.status_code == 200:
            filename_from_href = os.path.basename(pdf_url)
            valid_filename = get_valid_filename(pdf_name)
            file_ext = os.path.splitext(pdf_url)[1]
            file_name = f"{valid_filename}{file_ext}"
            rule_check_pdf(category, pdf_response.content, file_name)
            print(f"Downloaded: {pdf_name} => {file_name}")
        else:
            print(f"Failed to download: {pdf_url}")
