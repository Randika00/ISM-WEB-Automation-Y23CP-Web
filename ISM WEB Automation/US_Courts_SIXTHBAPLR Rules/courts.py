import requests
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys
import common_module

source_id = 'US_Courts_SIXTHBAPLR_Rules'
location_id = 'Local Rules'

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
    'Bankruptcy Rules': 'https://www.ca6.uscourts.gov/bankruptcy-appellate-panel-hearing-calendar'
}


for rule_name, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    pdf_folder = 'out'
    os.makedirs(pdf_folder, exist_ok=True)
    error_dict = {}
    error_list = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    table_content = soup.find('table', class_='views-view-grid')
    div_element = table_content.findAll('div')
    pdf_url = 'https://www.ca6.uscourts.gov/sites/ca6/files/documents/bap/calendar/Oral%20Argument%20Calendar.pdf'
    print(pdf_url)
    pdf_response = requests.get(pdf_url)
    output_fileName = common_module.ret_file_name_full(source_id, location_id, rule_name, '.pdf')
    with open(output_fileName, 'wb') as pdf_file:
        pdf_file.write(pdf_response.content)
    print(f"Downloaded: {output_fileName}")





