import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse


def rule_check_pdf(source_id, location_id, allowed_rules, ignore_rules, rule_name, pdf_content, file_name):
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


source_id_general_orders = 'USDC_BR_W_MOLR RULES'
location_id_general_orders = 'General Orders'
allowed_rules_general_orders = common_module.return_lists('links.txt')
ignore_rules_general_orders = common_module.return_lists('ignored_rules.txt')

source_id_local_rules = 'USDC_BR_W_MOLR RULES'
location_id_local_rules = 'Local Rules'
allowed_rules_local_rules = common_module.return_lists('links.txt')
ignore_rules_local_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'Western District of Missouri General Orders': 'https://www.mow.uscourts.gov/bankruptcy/rules',
    'Western District of Missouri Local Bankruptcy Rules': 'https://www.mow.uscourts.gov/bankruptcy/rules',
}

for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    if category == 'Western District of Missouri General Orders':
        li_elements = soup.find_all('li')
        for li_element in li_elements:
            links = li_element.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if '/sites/mow/files/' in href:
                    pdf_url = urllib.parse.urljoin(url, href)
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        pdf_name = link.get_text(strip=True)
                        output_file_name = format_pdf_name(pdf_name)
                        rule_check_pdf(source_id_general_orders, location_id_general_orders,
                                       allowed_rules_general_orders, ignore_rules_general_orders, pdf_name,
                                       response.content, output_file_name)
                    else:
                        print(f"Failed to download: {pdf_url}")

    elif category == 'Western District of Missouri Local Bankruptcy Rules':
        p_elements = soup.find_all('p')
        for p_element in p_elements:
            links = p_element.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if '/sites/mow/files/' in href:
                    pdf_url = urllib.parse.urljoin(url, href)
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        pdf_name = link.get_text(strip=True)
                        output_file_name = format_pdf_name(pdf_name)
                        rule_check_pdf(source_id_local_rules, location_id_local_rules, allowed_rules_local_rules,
                                       ignore_rules_local_rules, pdf_name, response.content, output_file_name)
                    else:
                        print(f"Failed to download: {pdf_url}")
