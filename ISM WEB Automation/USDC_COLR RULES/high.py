import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

# Processing General Orders
source_id_general_orders = 'USDC_COLR RULES'
location_id_general_orders = 'General Orders'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

general_orders_link = {
    'Middle District of Florida General Orders': 'http://www.cod.uscourts.gov/CourtOperations/OrdersandOpinions/CourtPlansandGeneralOrders.aspx',
}

def rule_check_pdf_general_orders(rule_name, pdf_content, file_name):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)

    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id_general_orders, cleaned_rule_title_new)

        output_file_name = common_module.ret_file_name_full(source_id_general_orders, location_id_general_orders, file_name, '.pdf')
        with open(output_file_name, 'wb') as file:
            file.write(pdf_content)
        print(f"Downloaded: {output_file_name}")

def format_pdf_name(pdf_name):
    # Replace '.' and ';' with ' ' and then insert '.' after the first sequence of digits
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"

for category, url in general_orders_link.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    p_elements = soup.find_all('p')

    for p_element in p_elements:
        try:
            links = p_element.find_all('a', href=True)
            for link in links:
                href = link['href']
                if '/Portals/0/Documents/Orders/' in href:
                    pdf_url = urllib.parse.urljoin(url, href)
                    print(f"Downloading: {pdf_url}")
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        pdf_name = link.get_text(strip=True)
                        output_file_name = format_pdf_name(pdf_name)
                        rule_check_pdf_general_orders(pdf_name, response.content, output_file_name)
                    else:
                        print(f"Failed to download: {pdf_url} - Status Code: {response.status_code}")
        except Exception as e:
            print(f"Exception occurred: {str(e)}")

# Processing Local Rules of Practice
source_id_local_rules = 'USDC_COLR RULES'
location_id_local_rules = 'Local Rules of Practice'

local_rules_link = {
    'Middle District of Florida Local Bankruptcy Rules': 'http://www.cod.uscourts.gov/CourtOperations/RulesProcedures/LocalRules.aspx',
}

for category, url in local_rules_link.items():
    pdf_url = 'http://www.cod.uscourts.gov/Portals/0/Documents/LocalRules/2023_Final_Local_Rules.pdf?ver=2023-11-30-151030-573'
    print(pdf_url)
    pdf_response = requests.get(pdf_url)
    pdf_name = "Local Rules effective December 1, 2023"  # Set the desired PDF name
    output_file_name = common_module.ret_file_name_full(source_id_local_rules, location_id_local_rules, format_pdf_name(pdf_name), '.pdf')
    with open(output_file_name, 'wb') as pdf_file:
        pdf_file.write(pdf_response.content)
    print(f"Downloaded: {output_file_name}")
