import os
import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id = 'USDC_BR_M_ALLR RULES'

# Define the functions
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


def format_pdf_name(pdf_name):
    # Replace '.' and ';' with ' ' and then insert '.' after the first sequence of digits
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"


def download_pdfs(url, location_id):
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    p_elements = soup.find_all('p')

    for p_element in p_elements:
        strong_elements = p_element.find_all('strong')

        for strong_element in strong_elements:
            link = strong_element.find('a')
            if link and 'href' in link.attrs:
                pdf_page_url = 'https://www.almb.uscourts.gov/' + link['href']

                try:
                    pdf_page_response = requests.get(pdf_page_url, timeout=10)
                    pdf_page_response.raise_for_status()

                    pdf_soup = BeautifulSoup(pdf_page_response.text, "html.parser")

                    pdf_links = pdf_soup.find_all('a', href=re.compile(".pdf"))

                    for pdf_link in pdf_links:
                        pdf_href = pdf_link.get('href')
                        if pdf_href.startswith('http'):
                            pdf_download_url = pdf_href
                        else:
                            pdf_download_url = urllib.parse.urljoin(pdf_page_url, pdf_href)

                        pdf_response = requests.get(pdf_download_url, stream=True, timeout=10)
                        pdf_response.raise_for_status()

                        filename_from_href = pdf_link.text.strip()
                        valid_filename = format_pdf_name(filename_from_href)
                        file_ext = os.path.splitext(pdf_download_url)[1]
                        file_name = f"{valid_filename}{file_ext}"
                        rule_check_pdf(filename_from_href, pdf_response.content, file_name, location_id)
                        print(f"Downloaded: {file_name}")

                except requests.RequestException as e:
                    print(f"Failed to fetch or download PDFs: {str(e)}")

# Constants
location_urls = {
    'Local Bankruptcy Rules': 'https://www.almb.uscourts.gov/local-rules-and-administrative-orders',
    'Administrative Orders': 'https://www.almb.uscourts.gov/adminorders',
}

# Load lists
allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')


for location_id, location_url in location_urls.items():
    download_pdfs(location_url, location_id)