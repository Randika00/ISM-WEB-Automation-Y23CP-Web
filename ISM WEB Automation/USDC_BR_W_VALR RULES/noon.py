import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id = 'USDC_BR_W_VALR RULES'
location_id = 'Local Rules and Orders'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'Western District of Virginia Local Bankruptcy Rules': 'http://www.vawb.uscourts.gov/?q=court-info/local-rules-and-orders',
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


def format_pdf_name(pdf_name):
    # Replace '.' and ';' with ' ' and then insert '.' after the first sequence of digits
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"


for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    span_elements = soup.find_all('span')

    for span_element in span_elements:
        try:
            links = span_element.find_all('a', href=True)
            for link in links:
                href = link['href']
                if 'sites/default/files/' in href:
                    pdf_url = urllib.parse.urljoin(url, href)
                    print(f"Downloading: {pdf_url}")
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        pdf_name = link.get_text(strip=True)
                        output_file_name = format_pdf_name(pdf_name)
                        rule_check_pdf(pdf_name, response.content, output_file_name)
                    else:
                        print(f"Failed to download: {pdf_url} - Status Code: {response.status_code}")
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            # Handle the exception as needed, e.g., continue the loop or break
