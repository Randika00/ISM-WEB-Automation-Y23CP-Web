import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id_standing_orders = 'USDC_E_CALR RULES'
location_id_standing_orders = 'Standing Orders'
source_id_general_orders = 'USDC_E_CALR RULES'
location_id_general_orders = 'General Orders'
source_id_local_rules = 'USDC_E_CALR RULES'
location_id_local_rules = 'Local Rules'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'Eastern District of California General Orders 01': 'https://www.caed.uscourts.gov/caednew/index.cfm/rules/general-orders/general-orders-a-50/',
    'Eastern District of California General Orders 02': 'https://www.caed.uscourts.gov/caednew/index.cfm/rules/general-orders/general-orders-51-100/',
    'Eastern District of California General Orders 03': 'https://www.caed.uscourts.gov/caednew/index.cfm/rules/general-orders/general-orders-501-550/',
    'Eastern District of California Standing Orders*': 'https://www.caed.uscourts.gov/caednew/index.cfm/rules/standing-orders/',
    'Eastern District of California Local Rules': 'https://www.caed.uscourts.gov/caednew/index.cfm/rules/local-rules/',
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


def format_pdf_name(pdf_name):
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"  # Removed ".pdf" part


for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    if 'Standing Orders' in category:
        ul_elements = soup.find_all('ul')
        for ul_element in ul_elements:
            try:
                links = ul_element.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if '/caednew/assets/File/' in href:
                        pdf_url = urllib.parse.urljoin(url, href)
                        print(f"Downloading Standing Orders: {pdf_url}")
                        response = requests.get(pdf_url)
                        if response.status_code == 200:
                            pdf_name = link.get_text(strip=True)
                            output_file_name = format_pdf_name(pdf_name)
                            rule_check_pdf(source_id_standing_orders, location_id_standing_orders, pdf_name,
                                           response.content, output_file_name)
                        else:
                            print(
                                f"Failed to download Standing Orders: {pdf_url} - Status Code: {response.status_code}")
            except Exception as e:
                print(f"Exception occurred: {str(e)}")

    elif 'Local Rules' in category:
        p_elements = soup.find_all('p')
        for p_element in p_elements:
            try:
                links = p_element.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if '/caednew/assets/File/' in href:
                        pdf_url = urllib.parse.urljoin(url, href)
                        print(f"Downloading Local Rules: {pdf_url}")
                        response = requests.get(pdf_url)
                        if response.status_code == 200:
                            pdf_name = link.get_text(strip=True)
                            output_file_name = format_pdf_name(pdf_name)
                            rule_check_pdf(source_id_local_rules, location_id_local_rules, pdf_name, response.content,
                                           output_file_name)
                        else:
                            print(f"Failed to download Local Rules: {pdf_url} - Status Code: {response.status_code}")
            except Exception as e:
                print(f"Exception occurred: {str(e)}")

    else:
        tr_elements = soup.find_all('tr')
        for tr_element in tr_elements:
            try:
                links = tr_element.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if '/caednew/assets/File/GeneralOrders/' in href:
                        pdf_url = urllib.parse.urljoin(url, href)
                        print(f"Downloading General Orders: {pdf_url}")
                        response = requests.get(pdf_url)
                        if response.status_code == 200:
                            pdf_name = link.get_text(strip=True)
                            output_file_name = format_pdf_name(pdf_name)
                            rule_check_pdf(source_id_general_orders, location_id_general_orders, pdf_name,
                                           response.content, output_file_name)
                        else:
                            print(f"Failed to download General Orders: {pdf_url} - Status Code: {response.status_code}")
            except Exception as e:
                print(f"Exception occurred: {str(e)}")
