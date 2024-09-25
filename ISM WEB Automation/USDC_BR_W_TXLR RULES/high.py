import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id = 'USDC_BR_W_TXLR RULES'
location_id_local_rules = 'Local Rules'

source_id = 'USDC_BR_W_TXLR RULES'
location_id_standing_orders = 'Standing Orders'

source_id = 'USDC_BR_W_TXLR RULES'
location_id_archived_standing_orders = 'Archived Standing Orders'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links_local_rules = {
    'Western District of Texas Local Bankruptcy Rules': 'https://www.txwb.uscourts.gov/local-rules',
}

sheet_links_standing_orders = {
    'Western District of Texas Standing Orders': 'https://www.txwb.uscourts.gov/standing-orders-index',
}

sheet_links_archived_standing_orders = {
    'Western District of Texas Archived Standing Orders': 'https://www.txwb.uscourts.gov/archived-standing-orders',
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

def format_pdf_name(pdf_name):
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"  # Removed ".pdf" part

def fetch_pdf(url, location_id):
    try:
        resource = requests.get(url, timeout=10)  # Set a timeout of 10 seconds
        soup = BeautifulSoup(resource.text, "html.parser")

        if location_id == location_id_local_rules:
            div_content = soup.find('div', class_='field__items')
            if div_content:
                links = div_content.find_all('a', href=True)
                for link in links:
                    href = link.get('href')
                    if '/sites/txwb/files' in href:
                        pdf_url = urllib.parse.urljoin(url, href)
                        response = requests.get(pdf_url, timeout=10)  # Set a timeout for PDF download
                        if response.status_code == 200:
                            pdf_name = link.get_text(strip=True)
                            output_file_name = format_pdf_name(pdf_name)
                            rule_check_pdf(pdf_name, response.content, output_file_name, location_id_local_rules)
                        else:
                            print(f"Failed to download: {pdf_url}")

        elif location_id == location_id_standing_orders:
            tr_elements = soup.find_all('tr')
            for tr_element in tr_elements:
                links = tr_element.find_all('a', href=True)
                for link in links:
                    href = link.get('href')
                    if '/sites/txwb/files/' in href:
                        pdf_url = urllib.parse.urljoin(url, href)
                        response = requests.get(pdf_url, timeout=10)  # Set a timeout for PDF download
                        if response.status_code == 200:
                            pdf_name = link.get_text(strip=True)
                            output_file_name = format_pdf_name(pdf_name)
                            rule_check_pdf(pdf_name, response.content, output_file_name, location_id_standing_orders)
                        else:
                            print(f"Failed to download: {pdf_url}")

        elif location_id == location_id_archived_standing_orders:
            tr_elements = soup.find_all('tr')
            for tr_element in tr_elements:
                links = tr_element.find_all('a', href=True)
                for link in links:
                    href = link.get('href')
                    if '/sites/txwb/files/' in href:
                        pdf_url = urllib.parse.urljoin(url, href)
                        response = requests.get(pdf_url, timeout=10)  # Set a timeout for PDF download
                        if response.status_code == 200:
                            pdf_name = link.get_text(strip=True)
                            output_file_name = format_pdf_name(pdf_name)
                            rule_check_pdf(pdf_name, response.content, output_file_name, location_id_archived_standing_orders)
                        else:
                            print(f"Failed to download: {pdf_url}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")

for category, url in sheet_links_local_rules.items():
    fetch_pdf(url, location_id_local_rules)

for category, url in sheet_links_standing_orders.items():
    fetch_pdf(url, location_id_standing_orders)

for category, url in sheet_links_archived_standing_orders.items():
    fetch_pdf(url, location_id_archived_standing_orders)
