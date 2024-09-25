import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id = 'USDC_BR_M_FLLR RULES'
location_id = 'Local Rules'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'Middle District of Florida Local Bankruptcy Rules': 'http://www.flmb.uscourts.gov/localrules/',
    'Administrative Orders': 'https://pacer.flmb.uscourts.gov/administrativeorders/search.asp'
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
    return f"{formatted_name.strip()}"  # Removed ".pdf" part


for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    if category == 'Middle District of Florida Local Bankruptcy Rules':
        a_elements = soup.find_all('a', href=True)

        for a_element in a_elements:
            if a_element['href'].endswith('.pdf'):
                pdf_url = urllib.parse.urljoin(url, a_element['href'])
                pdf_name = a_element.get_text(strip=True)
                output_file_name = format_pdf_name(pdf_name)

                response = requests.get(pdf_url)
                if response.status_code == 200:
                    rule_check_pdf(pdf_name, response.content, output_file_name)
                else:
                    print(f"Failed to download: {pdf_url}")

    elif category == 'Administrative Orders':
        p_elements = soup.find_all('p')
        for p_element in p_elements:
            links = p_element.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if 'DataFileOrder.asp?FileID=' in href:
                    pdf_url = urllib.parse.urljoin(url, href)
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        pdf_name = link.get_text(strip=True)
                        output_file_name = format_pdf_name(pdf_name)
                        rule_check_pdf(pdf_name, response.content, output_file_name)
                    else:
                        print(f"Failed to download: {pdf_url}")
