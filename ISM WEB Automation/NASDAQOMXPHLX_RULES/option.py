import requests
from bs4 import BeautifulSoup
import common_module
import re

source_id = 'NASDAQOMXPHLX_RULE'
location_id = 'Options Rules'

allowed_rules = []
ignore_rules = []

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'General': 'https://listingcenter.nasdaq.com/rulebook/phlx/rules',
}


def sanitize_rule_name(rule_name):
    # Remove invalid characters from the rule name
    return re.sub(r'[\/:*?"<>|]', '_', rule_name)

def rule_check(rule_name, html_content):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)
    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id, cleaned_rule_title_new)
        output_fimeName=common_module.ret_file_name_full(source_id,location_id,cleaned_rule_title_new,'.html')
        with open(output_fimeName, 'w', encoding='utf-8') as file:
            file.write(str(html_content))
            print(output_fimeName)

for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    ul_element = soup.findAll('ul')

    for item in ul_element:
        li_element = item.findAll('li')
        for i in li_element:
            try:
                name = str(i.text)
                if i.find('a'):
                   rule_url = 'https://listingcenter.nasdaq.com/' + i.find('a').get('href')
                   rule_response = requests.get(rule_url, allow_redirects=False)
                   if rule_response.status_code == 200:
                       rule_html = rule_response.text
                       rule_soup = BeautifulSoup(rule_html, "html.parser")

                       content = rule_soup.find('div', class_='rulebook-rules-container')

                       if content:
                            rule_header = content.find('div', {'class': 'rulebook-rules-header'})
                            if rule_header:
                                rule_name = rule_header.text
                                sanitized_rule_name = sanitize_rule_name(rule_name)
                                output_file_name = common_module.ret_file_name_full(source_id, location_id,
                                                                                    sanitized_rule_name, '.html')
                                rule_check(rule_name,content)

                                print(f"Downloaded HTML for rule '{rule_name}' at URL: {rule_url}")
                            else:
                                print(f"Rule header not found for URL: {rule_url}")
            except Exception as e:
                print(f"Error downloading HTML for URL: {rule_url}. Error: {str(e)}")




