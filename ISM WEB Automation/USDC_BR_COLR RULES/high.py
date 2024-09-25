import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id = 'USDC_BR_COLR RULES'
location_id = 'General Procedure Orders'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'District of Colorado Local Bankruptcy Rules - General Procedure Orders 01': 'https://www.cob.uscourts.gov/court-info/local-rules-and-orders/general-orders',
    'District of Colorado Local Bankruptcy Rules - General Procedure Orders 02': 'https://www.cob.uscourts.gov/court-info/local-rules-and-orders/general-orders?page=1',
    'District of Colorado Local Bankruptcy Rules - General Procedure Orders 03': 'https://www.cob.uscourts.gov/court-info/local-rules-and-orders/general-orders?page=2',
    'District of Colorado Local Bankruptcy Rules - General Procedure Orders 04': 'https://www.cob.uscourts.gov/court-info/local-rules-and-orders/general-orders?page=3',
    'District of Colorado Local Bankruptcy Rules - General Procedure Orders 05': 'https://www.cob.uscourts.gov/court-info/local-rules-and-orders/general-orders?page=4',
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


def format_pdf_name(pdf_name, text_content):
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"


for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    div_content = soup.find('div', class_='view-content')

    if div_content:
        links = div_content.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            if '/sites/default/files/' in href:
                pdf_url = urllib.parse.urljoin(url, href)
                response = requests.get(pdf_url)
                if response.status_code == 200:
                    pdf_name = link.get_text(strip=True)
                    output_file_name = format_pdf_name(pdf_name, "")
                    rule_check_pdf(pdf_name, response.content, output_file_name)
                else:
                    print(f"Failed to download: {pdf_url}")
