import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id_1 = 'USDC_BR_N_INLR RULES'
location_id_1 = 'Local Rules'

source_id_2 = 'USDC_BR_N_INLR RULES'
location_id_2 = 'General Orders'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'Local Bankruptcy Rules': 'https://www.innb.uscourts.gov/court-info/local-rules-and-orders/local-rules',
    'General Orders': 'https://www.innb.uscourts.gov/court-info/local-rules-and-orders/general-orders',
}

def rule_check_pdf(rule_name, pdf_content, file_name, source_id, location_id):
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

# Function to fetch PDFs with retry mechanism
def fetch_pdf_with_retry(pdf_url):
    retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        response = session.get(pdf_url, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")
        return None

# Fetching PDFs from Local Bankruptcy Rules
for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    if category == 'Local Bankruptcy Rules':
        div_content = soup.find('div', class_='view-content')
        if div_content:
            links = div_content.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if '/sites/innb/files/local_rules/' in href:
                    pdf_url = urllib.parse.urljoin(url, href)
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        pdf_name = link.get_text(strip=True)
                        output_file_name = format_pdf_name(pdf_name)
                        rule_check_pdf(pdf_name, response.content, output_file_name, source_id_1, location_id_1)
                    else:
                        print(f"Failed to download: {pdf_url}")

# Fetching PDFs from General Orders
for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    if category == 'General Orders':
        a_elements = soup.find_all('a', href=True)
        for a_element in a_elements:
            if a_element['href'].endswith('.pdf'):
                pdf_url = urllib.parse.urljoin(url, a_element['href'])
                pdf_name = a_element.get_text(strip=True)
                output_file_name = format_pdf_name(pdf_name)

                try:
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        rule_check_pdf(pdf_name, response.content, output_file_name, source_id_2, location_id_2)
                    else:
                        print(f"Failed to download: {pdf_url}")
                except requests.exceptions.RequestException as e:
                    print(f"Request Exception: {e}")
