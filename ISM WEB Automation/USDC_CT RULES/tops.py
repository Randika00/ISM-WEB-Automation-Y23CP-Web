import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id = 'USDC_CT RULES'
allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

# Define functions for rule checking and formatting PDF names
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
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"  # Removed ".pdf" part

# Processing for the first set of links
def process_links_1(url, location_id):
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    elements = soup.find_all('a', href=True)

    for element in elements:
        try:
            href = element['href']
            if '/file/' in href or '/sites/default/files/adminOrdersOCR/' in href:
                pdf_url = urllib.parse.urljoin(url, href)
                print(f"Downloading: {pdf_url}")
                response = requests.get(pdf_url)
                if response.status_code == 200:
                    pdf_name = element.get_text(strip=True)
                    output_file_name = format_pdf_name(pdf_name)
                    rule_check_pdf(pdf_name, response.content, output_file_name, location_id)
                else:
                    print(f"Failed to download: {pdf_url} - Status Code: {response.status_code}")
        except Exception as e:
            print(f"Exception occurred: {str(e)}")

# First set of URLs to process with corresponding location IDs
sheet_links_1 = {
    'District of Connecticut Local Rules of Civil Procedure': ('https://www.ctd.uscourts.gov/administrative-standing-orders', 'Administrative & Standing Orders'),
    'District of Connecticut Local Rules of Practice & Procedure': ('https://www.uscourts.gov/rules-policies/current-rules-practice-procedure', 'Local Rules'),
}

# Processing each link in the first set
for category, link_data in sheet_links_1.items():
    url, location_id = link_data
    process_links_1(url, location_id)

# Processing for the second set of links
def process_links_2(url, location_id):
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    p_elements = soup.find_all('p')
    pdf_url = 'https://www.ctd.uscourts.gov/sites/default/files/Revised-Local-Rules-10.19.23.pdf'
    print(pdf_url)
    pdf_response = requests.get(pdf_url)
    pdf_name = "United States District Court of Connecticut Local Rules"
    output_file_name = common_module.ret_file_name_full(source_id, location_id, format_pdf_name(pdf_name), '.pdf')
    with open(output_file_name, 'wb') as pdf_file:
        pdf_file.write(pdf_response.content)
    print(f"Downloaded: {output_file_name}")

# Second set of URLs to process with corresponding location ID
sheet_links_2 = {
    'District of Connecticut Local Rules of Civil Procedure': 'https://www.ctd.uscourts.gov/court-info/local-rules-and-orders',
}

# Processing each link in the second set
for category, url in sheet_links_2.items():
    process_links_2(url, 'Local Rules')


