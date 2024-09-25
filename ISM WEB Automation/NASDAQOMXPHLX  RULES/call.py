import requests
from bs4 import BeautifulSoup
import common_module
import re

source_id = 'NASDAQOMXPHLX_RULE'
location_id = 'General Rules'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('skip.txt')

sheet_links = {
    'General': 'https://listingcenter.nasdaq.com/rulebook/phlx/rules',
}


def sanitize_rule_name(rule_name):
    # Remove invalid characters from the rule name
    return re.sub(r'[\/:*?"<>|]', '_', rule_name)


for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    table_content = soup.find('table', class_='rules-table-content')
    table = table_content.findAll('tr')

    for item in table:
        td_element = item.findAll('td')
        for i in td_element:
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
                                with open(output_file_name, 'w', encoding='utf-8') as f:
                                    f.write(str(content))

                                print(f"Downloaded HTML for rule '{rule_name}' at URL: {rule_url}")
                            else:
                                print(f"Rule header not found for URL: {rule_url}")
            except Exception as e:
                print(f"Error downloading HTML for URL: {rule_url}. Error: {str(e)}")