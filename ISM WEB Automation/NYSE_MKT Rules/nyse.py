import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime
import os
import sys

source_id = 'NYSE_MKT Rules'

allow_rules = []
try:
    with open('allow_rules.txt', 'r', encoding='utf-8') as my_file:
        allowed_rules = my_file.readlines()
except FileNotFoundError:
    print("File 'links.txt' not found. Please make sure it exists.")
allowed_rules = [rule.strip().replace('â€ƒ', ' ').replace('â€‰', ' ') for rule in allowed_rules]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

sheet_links = {
    ' NYSE RULES ': 'https://nyseguide.srorules.com/rules'
}

for rule_name, url in sheet_links.items():
    resource = requests.get(url, headers=headers)
    soup = BeautifulSoup(resource.text, "html.parser")


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

section = soup.find('section', class_="cg-card-container-1-10-0")

ul_element = section.findAll('ul')
li_element = section.findAll('li')

ul_element.extend(li_element)

for i in ul_element:
    link = i.find('a', href=True)
    if link:
        rule_url = 'https://nyseguide.srorules.com/rules/' + link['href']

        filename = os.path.basename(rule_url)

        if filename.endswith('.docx'):
            rule_response = requests.get(rule_url)
            if rule_response.status_code == 200:

                out_folder = ret_out_folder(source_id, 'NYSE RULES')
                full_path = ret_file_name_full(source_id, 'NYSE RULES', filename, '.docx')
                if not os.path.exists(out_folder):
                    os.makedirs(out_folder)
                with open(full_path, 'wb') as f:
                    f.write(rule_response.content)
                print(f"Downloaded: {filename}")

            else:
                print(f"Failed to download: {filename}")
