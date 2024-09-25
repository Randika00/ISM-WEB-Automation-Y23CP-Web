import os
import requests
from bs4 import BeautifulSoup
import common_module
import re

source_id = 'USDC_BR_GULR RULES'
location_id = 'Local Rules'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'Local Rules of Practice Rules': 'https://www.gud.uscourts.gov/Local_Rules_of_Practice',
}

downloaded_files = set()

def rule_check_pdf(rule_name, pdf_content, file_name):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)

    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id, cleaned_rule_title_new)
            downloaded_files.add(file_name)  # Add file name to the set

        output_file_name = common_module.ret_file_name_full(source_id, location_id, file_name, '.pdf')
        with open(output_file_name, 'wb') as file:
            file.write(pdf_content)
            print(f"Downloaded: {output_file_name}")

def get_valid_filename(s):
    return "".join([c for c in s if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()

for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    ul_elements = soup.find_all('ul')

    for ul_element in ul_elements:
        li_elements = ul_element.find_all('li')

        for li in li_elements:
            link = li.find('a')

            if link and link['href'].endswith('.pdf'):
                pdf_url = 'https://www.gud.uscourts.gov/' + link['href']
                pdf_response = requests.get(pdf_url, stream=True)

                if pdf_response.status_code == 200:
                    filename_from_href = link.text.strip()
                    valid_filename = get_valid_filename(filename_from_href)
                    file_ext = os.path.splitext(pdf_url)[1]
                    file_name = f"{valid_filename}{file_ext}"
                    rule_check_pdf(category, pdf_response.content, file_name)
                    print(f"Downloaded: {file_name}")
                else:
                    print(f"Failed to download: {pdf_url}")

# I try to Write unique downloaded file names in here
if downloaded_files:
    out_folder = 'out'
    new_rules_path = os.path.join(out_folder, 'new_rules.txt')
    with open(new_rules_path, 'w') as new_rules_file:
        for file_name in downloaded_files:
            new_rules_file.write(file_name + '\n')