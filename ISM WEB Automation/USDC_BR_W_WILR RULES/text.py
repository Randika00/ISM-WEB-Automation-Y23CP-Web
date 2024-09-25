import requests
import common_module
import re
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys

source_id = 'USDC_BR_W_WILR RULES'
location_id = 'Local Rules'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')


def rule_check_html(rule_name, html_content):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)
    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id, cleaned_rule_title_new)
        output_file_name = common_module.ret_file_name_full(source_id, location_id, cleaned_rule_title_new, '.html')
        with open(output_file_name, 'w', encoding='utf-8') as file:
            file.write(str(html_content))
            print(output_file_name)


def ret_out_folder(source_id, location_id):
    exe_folder = os.path.dirname(str(os.path.abspath(sys.argv[0])))
    date_prefix = datetime.today().strftime("%Y%m%d")
    out_path = os.path.join(exe_folder, 'out', remove_invalid_paths(source_id), 'Skip Rules',
                            remove_invalid_paths(location_id), date_prefix)
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    return out_path


def format_html_name(html_name):
    # Replace any unwanted characters with spaces and then remove extra spaces
    formatted_name = re.sub(r'[^\w\s]', ' ', html_name)
    formatted_name = re.sub(r'\s+', ' ', formatted_name.strip())
    return formatted_name


def remove_invalid_paths(path_val):
    return re.sub(r'[\\/*?:"<>|]', "", path_val)


sheet_links = {
    'Western District of Wisconsin Local Bankruptcy Rules': 'https://www.wiwb.uscourts.gov/court-info/local-rules-and-orders'

}

for rule_name, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    div_content = soup.find('div', class_='field__items')

    if div_content:
        html_content = str(div_content)

        file_extension = '.html'
        out_folder = ret_out_folder(source_id, location_id)
        file_name = common_module.ret_file_name_full(source_id, location_id, rule_name, file_extension)

        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(html_content)

        print(f"Downloaded HTML content for '{rule_name}' to {file_name}")
    else:
        print(f"Unable to find the 'center_box' div for '{rule_name}'")
