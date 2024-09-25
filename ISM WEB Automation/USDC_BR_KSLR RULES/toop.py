import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse
import time


def download_pdf_from_url(source_id, location_id, url):
    allowed_rules = common_module.return_lists('links.txt')
    ignore_rules = common_module.return_lists('ignored_rules.txt')

    def rule_check_pdf(rule_name, pdf_content, file_name):
        cleaned_rule_name = common_module.clean_rule_title(rule_name)
        cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
        cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)

        if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
            if not cleaned_rule_name in allowed_rules:
                common_module.append_new_rule(source_id, cleaned_rule_title_new)

            cleaned_file_name = re.sub(r'[^\w\s.-]', '_', file_name)[:150]
            output_file_name = common_module.ret_file_name_full(source_id, location_id, cleaned_file_name, '.pdf')

            with open(output_file_name, 'wb') as file:
                file.write(pdf_content)
                print(f"Downloaded: {output_file_name}")

    def format_pdf_name(pdf_name):
        formatted_name = re.sub(r'[.;]', ' ', pdf_name)
        formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
        return f"{formatted_name.strip()}"

    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")
    a_elements = soup.find_all('a', href=True)

    for a_element in a_elements:
        if a_element['href'].endswith('.pdf'):
            pdf_url = urllib.parse.urljoin(url, a_element['href'])
            pdf_name = a_element.get_text(strip=True)
            output_file_name = format_pdf_name(pdf_name)

            retries = 3  # Number of retries
            for attempt in range(retries):
                try:
                    response = requests.get(pdf_url, timeout=10)  # Adjust timeout as needed
                    if response.status_code == 200:
                        rule_check_pdf(pdf_name, response.content, output_file_name)
                        break  # Break the retry loop if successful
                except requests.exceptions.ReadTimeout as e:
                    print(f"Request timed out. Retrying... Attempt {attempt + 1} of {retries}")
                    time.sleep(5)
                except Exception as e:
                    print(f"An error occurred: {e}")
                    break
            else:
                print(f"Failed to download after {retries} attempts: {pdf_url}")


sheet_links = {
    'Local Rules for Kansas District Court': 'https://www.ksb.uscourts.gov/local-rules',
    'Standing Orders for Kansas District Court': 'https://www.ksb.uscourts.gov/standinggeneral-orders',
}

source_id = 'USDC_BR_KSLR RULES'
for category, url in sheet_links.items():
    location_id = 'Local Rules' if 'local' in url else 'Standing Orders Rules'
    download_pdf_from_url(source_id, location_id, url)
