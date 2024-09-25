import requests
from bs4 import BeautifulSoup
import common_module
import re

source_id = 'South Carolina State Court Rules'
location_id = 'Rules of Civil Procedure'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'South Carolina State Court Rules - Rules of Civil Procedure': 'https://www.sccourts.org/courtReg/index.cfm'
}


def rule_check_html(rule_name, html_content, file_name):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)

    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id, cleaned_rule_title_new)

        output_file_name = common_module.ret_file_name_full(source_id, location_id, file_name, '.html')
        with open(output_file_name, 'w') as file:
            file.write(html_content)
            print(f"Downloaded: {output_file_name}")


for category, url in sheet_links.items():
    retries = 3  # Number of retries
    for attempt in range(retries):
        try:
            resource = requests.get(url, timeout=15)  # Increased timeout to 15 seconds
            if resource.status_code == 200:
                soup = BeautifulSoup(resource.text, "html.parser")
                # Process the HTML content or call function to handle it
                break  # If successful, exit the loop
            else:
                print(f"Failed to fetch data from {url}. Status code: {resource.status_code}")
        except requests.RequestException as e:
            print(f"Error accessing {url}: {e}")
        if attempt < retries - 1:
            print(f"Retrying... Attempt {attempt + 1}")
