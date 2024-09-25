import requests
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys

source_id='US_Courts_VCLR_Rules'
location_id = 'Court Forms'

def ret_file_name_full(source_id, location_id, rule_name, extention):
    exe_folder = os.path.dirname(str(os.path.abspath(sys.argv[0])))
    date_prefix = datetime.today().strftime("%Y%m%d")
    out_path = os.path.join(exe_folder, 'out', remove_invalid_paths(source_id), remove_invalid_paths(location_id),
                            (date_prefix))
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    index = 1
    outFileName = os.path.join(out_path, remove_invalid_paths(rule_name) + extention)
    retFileName = outFileName
    while os.path.isfile(retFileName):
        retFileName = os.path.join(out_path, remove_invalid_paths(rule_name) + "_" + str(index) + extention)
    index += 1
    return retFileName

def ret_out_folder(source_id, location_id):
    exe_folder = os.path.dirname(str(os.path.abspath(sys.argv[0])))
    date_prefix = datetime.today().strftime("%Y%m%d")
    out_path = os.path.join(exe_folder, 'out', remove_invalid_paths(source_id), 'Skip Rules',
                            remove_invalid_paths(location_id), date_prefix)
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    return out_path


def remove_invalid_paths(path_val):
    return re.sub(r'[\\/*?:"<>|]', "", path_val)

allow_rules = []
try:
    with open('allow_rules.txt', 'r', encoding='utf-8') as my_file:
        allowed_rules = my_file.readlines()
except FileNotFoundError:
    print("File 'allow_rules.txt' not found. Please make sure it exists.")
allowed_rules = [rule.strip().replace('â€ƒ', ' ').replace('â€‰', ' ') for rule in allowed_rules]

sheet_links = {
    'Complaint Form': 'http://www.uscourts.cavc.gov/forms_fees.php'

}

for rule_name, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    content = soup.find('div', {'id': 'content_subpage'})

    if content:
        html_content = str(content)

        file_extension = '.html'
        out_folder = ret_out_folder(source_id, location_id)
        file_name = ret_file_name_full(source_id, location_id, rule_name, file_extension)

        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(html_content)

        print(f"Downloaded HTML content for '{rule_name}' to {file_name}")
    else:
        print(f"Unable to find the 'center_box' div for '{rule_name}'")
