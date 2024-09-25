import requests
import os
from bs4 import BeautifulSoup
import common_module
import re

source_id = 'USCC_EIGHTBAPLR'
location_id = 'Local Rules'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'The Criminal Justice Law': 'https://www.ca8.uscourts.gov/rules-procedures',
    'The Criminal Justice Act': 'https://www.ca8.uscourts.gov/rules-procedures',
    'Local Rules of the Eighth Circuit': 'https://www.ca8.uscourts.gov/rules-procedures',
    'Research Aids Rules': 'https://www.ca8.uscourts.gov/rules-procedures',
    'Internal Operating Procedures': 'https://www.ca8.uscourts.gov/rules-procedures',
    'Practice and Procedure': 'https://www.uscourts.gov/rules-policies/current-rules-practice-procedure'
}

def rule_check(rule_name, pdf_content, file_name):
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

for rule_name, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    pdf_folder = 'out'
    os.makedirs(pdf_folder, exist_ok=True)

    if rule_name == 'Practice and Procedure':
        div_element = soup.find('div', class_='field field-name-body')
        h2_elements = div_element.find_all('h2')

        for h2 in h2_elements:
            rule_name = h2.text.strip()
            pdf_urls = []
            p_content = h2.find_next('p')

            link = p_content.find('a', href=True)
            if link:
                pdf_url = link['href']
                if not pdf_url.startswith(('http://', 'https://')):
                    pdf_url = 'https://www.uscourts.gov/' + pdf_url
                pdf_urls.append(pdf_url)

            for index, pdf_url in enumerate(pdf_urls, start=1):
                try:
                    pdf_response = requests.get(pdf_url)
                    if pdf_response.status_code == 200:
                        output_fileName = common_module.ret_file_name_full(source_id, location_id, rule_name, '.pdf')

                        if index > 1:
                            output_fileName = common_module.ret_file_name_full(source_id, location_id, f"{rule_name}_{index}", '.pdf')

                        with open(output_fileName, 'wb') as pdf_file:
                            pdf_file.write(pdf_response.content)
                        print(f"Downloaded: {output_fileName}")
                    else:
                        print(f"Failed to download: {pdf_url}")
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading PDF from {pdf_url}: {e}")
    else:
        div_content = soup.find('div', class_='field__item even')
        p_elements = div_content.findAll('p')

        if rule_name in ['The Criminal Justice Law', 'The Criminal Justice Act']:
            if rule_name == 'The Criminal Justice Law':
                pdf_url = 'http://media.ca8.uscourts.gov/newrules/coa/cjaplan.pdf'
            elif rule_name == 'The Criminal Justice Act':
                pdf_url = 'http://media.ca8.uscourts.gov/newrules/coa/Plan_V_Revision.pdf'
            print(pdf_url)
            pdf_response = requests.get(pdf_url)
            output_file_name = common_module.ret_file_name_full(source_id, location_id, rule_name, '.pdf')

            with open(output_file_name, 'wb') as pdf_file:
                pdf_file.write(pdf_response.content)

            print(f"Downloaded: {output_file_name}")
        else:
            if rule_name == 'Local Rules of the Eighth Circuit':
                pdf_url = 'http://media.ca8.uscourts.gov/newrules/coa/localrules.pdf'
            elif rule_name == 'Research Aids Rules':
                pdf_url = 'https://www.ca7.uscourts.gov/ftips/type.pdf'
            elif rule_name == 'Internal Operating Procedures':
                pdf_url = 'http://media.ca8.uscourts.gov/newrules/coa/iops06-19update.pdf'
            print(pdf_url)
            pdf_response = requests.get(pdf_url)
            output_file_name = common_module.ret_file_name_full(source_id, location_id, rule_name, '.pdf')

            with open(output_file_name, 'wb') as pdf_file:
                pdf_file.write(pdf_response.content)

            print(f"Downloaded: {output_file_name}")
