import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id = 'USDC_BR_M_GALR RULES'
allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

# Administrative Orders
location_id_admin = 'Administrative Orders'
sheet_links_admin = {
    'Middle District of Georgia Local Bankruptcy Rules': 'https://www.gamb.uscourts.gov/USCourts/administrative-orders',
}


def rule_check_pdf_admin(rule_name, pdf_content, file_name):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)

    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id, cleaned_rule_title_new)

        output_file_name = common_module.ret_file_name_full(source_id, location_id_admin, file_name, '.pdf')
        with open(output_file_name, 'wb') as file:
            file.write(pdf_content)
            print(f"Downloaded: {output_file_name}")


# Local Rules
location_id_local = 'Local Rules'
sheet_links_local = {
    'Middle District of Georgia Local Bankruptcy Rules': 'https://www.gamb.uscourts.gov/USCourts/local-rules-and-clerks-instructions',
}


def rule_check_pdf_local(rule_name, pdf_content, file_name):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)

    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id, cleaned_rule_title_new)

        output_file_name = common_module.ret_file_name_full(source_id, location_id_local, file_name, '.pdf')
        with open(output_file_name, 'wb') as file:
            file.write(pdf_content)
            print(f"Downloaded: {output_file_name}")


def format_pdf_name(pdf_name):
    # Replace '.' and ';' with ' ' and then insert '.' after the first sequence of digits
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"


# Processing Administrative Orders
for category, url in sheet_links_admin.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    ul_elements = soup.find_all('ul')
    for ul_element in ul_elements:
        links = ul_element.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            if 'https://www.gamb.uscourts.gov/' in href:
                pdf_url = urllib.parse.urljoin(url, href)
                response = requests.get(pdf_url)
                if response.status_code == 200:
                    pdf_name = link.get_text(strip=True)
                    output_file_name = format_pdf_name(pdf_name)
                    rule_check_pdf_admin(pdf_name, response.content, output_file_name)
                else:
                    print(f"Failed to download: {pdf_url}")

# Processing Local Rules
for category, url in sheet_links_local.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    p_elements = soup.find_all('p')
    pdf_url = 'https://www.gamb.uscourts.gov/USCourts/sites/default/files/local_rules/Local_Rules_Jan_2023.pdf'
    print(pdf_url)
    pdf_response = requests.get(pdf_url)
    pdf_name = "Local Rules"
    output_file_name = common_module.ret_file_name_full(source_id, location_id_local, format_pdf_name(pdf_name), '.pdf')
    with open(output_file_name, 'wb') as pdf_file:
        pdf_file.write(pdf_response.content)
    print(f"Downloaded: {output_file_name}")
