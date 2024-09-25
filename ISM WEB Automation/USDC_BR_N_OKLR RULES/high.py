import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id_admin = 'USDC_BR_N_OKLR RULES'
location_id_admin = 'General Orders'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links_admin = {
    'Northern District of Oklahoma Local Bankruptcy Rules': 'https://www.oknb.uscourts.gov/general-orders-all',
}

def rule_check_pdf_admin(rule_name, pdf_content, file_name):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)

    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id_admin, cleaned_rule_title_new)

        output_file_name = common_module.ret_file_name_full(source_id_admin, location_id_admin, file_name, '.pdf')
        with open(output_file_name, 'wb') as file:
            file.write(pdf_content)
            print(f"Downloaded: {output_file_name}")

def format_pdf_name_admin(pdf_name, td_text):
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}. {td_text}"

for category_admin, url_admin in sheet_links_admin.items():
    resource_admin = requests.get(url_admin)
    soup_admin = BeautifulSoup(resource_admin.text, "html.parser")

    tr_elements_admin = soup_admin.find_all('tr')
    for tr_element_admin in tr_elements_admin:
        td_element_admin = tr_element_admin.find('td', string=re.compile(r'ORDER Terminating General Order'))
        td_text_admin = td_element_admin.get_text(strip=True) if td_element_admin else ''
        links_admin = tr_element_admin.find_all('a', href=True)
        for link_admin in links_admin:
            href_admin = link_admin.get('href')
            if '/sites/oknb/files/' in href_admin:
                pdf_url_admin = urllib.parse.urljoin(url_admin, href_admin)
                response_admin = requests.get(pdf_url_admin)
                if response_admin.status_code == 200:
                    pdf_name_admin = link_admin.get_text(strip=True)
                    output_file_name_admin = format_pdf_name_admin(pdf_name_admin, td_text_admin)
                    rule_check_pdf_admin(pdf_name_admin, response_admin.content, output_file_name_admin)
                else:
                    print(f"Failed to download: {pdf_url_admin}")

source_id_local = 'USDC_BR_N_OKLR RULES'
location_id_local = 'Local Rules'

sheet_links_local = {
    'Northern District of Oklahoma Local Bankruptcy Rules': 'https://www.oknb.uscourts.gov/court-info/local-rules-and-orders',
}

def rule_check_pdf_local(rule_name, pdf_content, file_name):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)

    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id_local, cleaned_rule_title_new)

        output_file_name = common_module.ret_file_name_full(source_id_local, location_id_local, file_name, '.pdf')
        with open(output_file_name, 'wb') as file:
            file.write(pdf_content)
            print(f"Downloaded: {output_file_name}")

def format_pdf_name_local(pdf_name):
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"

for category_local, url_local in sheet_links_local.items():
    resource_local = requests.get(url_local)
    soup_local = BeautifulSoup(resource_local.text, "html.parser")

    ul_elements_local = soup_local.find_all('ul')
    pdf_url_local = 'https://www.oknb.uscourts.gov/sites/oknb/files/Local%20Rules.pdf'
    print(pdf_url_local)
    pdf_response_local = requests.get(pdf_url_local)
    pdf_name_local = "LOCAL BANKRUPTCY RULES"
    output_file_name_local = common_module.ret_file_name_full(source_id_local, location_id_local, format_pdf_name_local(pdf_name_local), '.pdf')
    with open(output_file_name_local, 'wb') as pdf_file_local:
        pdf_file_local.write(pdf_response_local.content)
    print(f"Downloaded: {output_file_name_local}")
