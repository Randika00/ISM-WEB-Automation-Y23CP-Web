import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id_archived = 'USDC_C_CALR RULES'
location_id_archived = 'Archived General Orders'
source_id_operative = 'USDC_C_CALR RULES'
location_id_operative = 'Operative General Orders'
source_id_local = 'USDC_C_CALR RULES'
location_id_local = 'Local Rules'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

archived_sheet_links = {
    'Central District of California Archived General Orders': 'http://www.cacd.uscourts.gov/court-procedures/general-orders/archives',
}

operative_sheet_links = {
    'Central District of California Operative General Orders': 'http://www.cacd.uscourts.gov/court-procedures/general-orders',
}

local_sheet_links = {
    'Central District of California Local Rules': 'http://www.cacd.uscourts.gov/court-procedures/local-rules',
}

def rule_check_pdf(source_id, location_id, rule_name, pdf_content, file_name):
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

def format_pdf_name(pdf_name, additional_text=''):
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    full_name = f"{formatted_name.strip()} {additional_text}".strip()
    return full_name  # Removed ".pdf" part

def process_sheet(sheet_links, source_id, location_id):
    for category, url in sheet_links.items():
        resource = requests.get(url)
        soup = BeautifulSoup(resource.text, "html.parser")
        tr_elements = soup.find_all('tr')

        for tr_element in tr_elements:
            try:
                links = tr_element.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if '/sites/default/files/' in href:
                        pdf_url = urllib.parse.urljoin(url, href)
                        print(f"Downloading: {pdf_url}")
                        response = requests.get(pdf_url)
                        if response.status_code == 200:
                            pdf_name = link.get_text(strip=True)
                            # Extract additional text from <p> tag if available
                            paragraph = tr_element.find_next('p')
                            additional_text = ''
                            if paragraph:
                                additional_text = paragraph.get_text(strip=True)
                            output_file_name = format_pdf_name(pdf_name, additional_text)
                            rule_check_pdf(source_id, location_id, pdf_name, response.content, output_file_name)
                        else:
                            print(f"Failed to download: {pdf_url} - Status Code: {response.status_code}")
            except Exception as e:
                print(f"Exception occurred: {str(e)}")

# Process Archived General Orders
process_sheet(archived_sheet_links, source_id_archived, location_id_archived)

# Process Operative General Orders
process_sheet(operative_sheet_links, source_id_operative, location_id_operative)

# Process Local Rules
sheet_links = {
    'Central District of California Local Rules': 'http://www.cacd.uscourts.gov/court-procedures/local-rules',
}

for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    a_elements = soup.find_all('a', href=True)

    for a_element in a_elements:
        if a_element['href'].endswith('.pdf'):
            pdf_url = urllib.parse.urljoin(url, a_element['href'])
            pdf_name = a_element.get_text(strip=True)
            output_file_name = format_pdf_name(pdf_name)

            response = requests.get(pdf_url)
            if response.status_code == 200:
                rule_check_pdf(source_id_local, location_id_local, pdf_name, response.content, output_file_name)
            else:
                print(f"Failed to download: {pdf_url}")
