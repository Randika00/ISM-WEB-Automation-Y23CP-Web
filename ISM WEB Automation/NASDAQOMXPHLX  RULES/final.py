import requests
from bs4 import BeautifulSoup
import json
import os
import re
import common_module

def compare_rule_name(rule_name,html_content):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)
    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name)>0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id, cleaned_rule_title_new)
        output_fimeName=common_module.ret_file_name_full(source_id,location_id,cleaned_rule_title_new,'.html')
        with open(output_fimeName, 'w', encoding='utf-8') as file:
            file.write(str(html_content))
            print(output_fimeName)

def get_rule(url,rule_name):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    desired_script = soup.find('script', id='__NEXT_DATA__')
    if desired_script:
        data = json.loads(desired_script.text)
        page_props = data.get("props", {})
        content_html = page_props.get("pageProps", {}).get("document", {}).get("section", {}).get("document", {}).get(
            "content", "")

        content_soup = BeautifulSoup(content_html, 'html.parser')

        div_ele = content_soup.find('div', class_='documentContent')
        last_p_with_class_hP = div_ele.find_all('p', class_='hP')[-1]
        last_p_with_class_hP.extract()
        last_p_with_class_hP = div_ele.find_all('p', class_='hP')[-1]
        last_p_with_class_hP.extract()
        last_p_with_class_hP = div_ele.find('button', {
            'class': 'wk-button wk-button-icon wk-button-small nyse-document-download-link'})
        last_p_with_class_hP.extract()
        compare_rule_name(rule_name,div_ele)

def new_function(url,rule_name):
    global combined_soup
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    desired_script = soup.find('script', id='__NEXT_DATA__')
    if desired_script:
        data = json.loads(desired_script.text)
        page_props = data.get("props", {})
        content_html = page_props.get("pageProps", {}).get("document", {}).get("section", {}).get("document", {}).get(
            "content", "")

        content_soup = BeautifulSoup(content_html, 'html.parser')

        div_ele = content_soup.find('div', class_='documentContent')
        last_p_with_class_hP = div_ele.find_all('p', class_='hP')[-1]
        last_p_with_class_hP.extract()
        last_p_with_class_hP = div_ele.find_all('p', class_='hP')[-1]
        last_p_with_class_hP.extract()
        last_p_with_class_hP = div_ele.find('button', {
            'class': 'wk-button wk-button-icon wk-button-small nyse-document-download-link'})
        last_p_with_class_hP.extract()

        combined_soup.append(div_ele)
        if rule_name=='Rule 5.5':
            compare_rule_name('Rule 5P SECURITIES LISTED AND TRADED',combined_soup)
            combined_soup = BeautifulSoup('', 'html.parser')
        if rule_name=='Rule 7.46. Tick Size Pilot Plan':
            compare_rule_name('Rule 7P EQUITIES TRADING',combined_soup)
            combined_soup = BeautifulSoup('', 'html.parser')
        if rule_name=='Rule 8.900. Managed Portfolio Shares':
            compare_rule_name('Rule 8P LISTING AND TRADING OF CERTAIN EXCHANGE TRADED PRODUCTS',combined_soup)
            combined_soup = BeautifulSoup('', 'html.parser')

def get_child(parent_nodes):
    for document in parent_nodes:
        try:
            children_nodes = document.get("children", [])
            if children_nodes:
                return children_nodes
            else:
                new_title1 = document.get("title")
                if not new_title1 in printed_rules:
                    rule_link=document.get("href")
                    if rule_link:
                        printed_rules.append(new_title1)
                        link = rule_link.replace("/browse/", "https://nyseguide.srorules.com/rules/")
                        new_url_list=['https://nyseguide.srorules.com/rules/eac951727d5f10009374005056881d2301',
                                      'https://nyseguide.srorules.com/rules/adabe2b07d5e100088ed005056881d2301',
                                      'https://nyseguide.srorules.com/rules/adabe2b07d5e1000b9e8005056881d2302',
                                      'https://nyseguide.srorules.com/rules/a8ee9cec7dde100089ae000d3a8bba6b04',
                                      'https://nyseguide.srorules.com/rules/855bd4507d5e1000b03e005056885db601',
                                      'https://nyseguide.srorules.com/rules/855bd4507d5e1000ab33005056885db602',
                                      'https://nyseguide.srorules.com/rules/52dd0a847d461000be34005056883b3a041',
                                      'https://nyseguide.srorules.com/rules/52dd0a847d46100089b9005056883b3a043',
                                      'https://nyseguide.srorules.com/rules/52dd0a987d461000ac9a005056883b3a044',
                                      'https://nyseguide.srorules.com/rules/eac9533e7d5f1000b447005056881d2302',
                                      'https://nyseguide.srorules.com/rules/e8937a5e7d5f1000a34e005056881d2306',
                                      'https://nyseguide.srorules.com/rules/e8937afe7d5f100093d4005056881d23014']
                        if url in new_url_list:
                            new_function(link,new_title1)
                        else:
                            get_rule(link, new_title1)

        except Exception as error:
            common_module.append_error(source_id, error)

source_id = 'NYSE_Rules'
location_id='Rules'

printed_rules=[]
allowed_rules = []
ignore_rules = []

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
}
combined_soup = BeautifulSoup('', 'html.parser')
if os.path.exists('links.txt') and os.path.exists('ignored_rules.txt') and os.path.exists('Sub_links.txt') and os.path.exists('common_module.py'):
    try:
        with open('Sub_links.txt', 'r') as file:
            url_list = [line.strip() for line in file]
    except Exception as error:
        common_module.append_error(source_id, error)

    for url in url_list:
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            desired_script = soup.find('script', id='__NEXT_DATA__')

            if desired_script:
                data = json.loads(desired_script.text)
                page_props = data.get("props", {})
                all_parent_nodes = page_props.get("pageProps", {}).get("allParentNodes", [])

                i=0
                while i<10:
                    all_parent_nodes=get_child(all_parent_nodes)
                    if all_parent_nodes:
                        i=0
                    else:
                        i=20
            else:
                print("Script with id '__NEXT_DATA__' not found in the HTML.")

        except Exception as error:
            common_module.append_error(source_id, error)

else:
    print("'links.txt' or 'ignored_rules.txt' or 'Sub_links.txt' or 'common_module.py' does not exist in the current directory.")
