import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
import re
import sys
from datetime import datetime
import common_module


source_id='Arizona_SCR'
def skip_rule_file(source_id,location_id, rule_name,extention):
    exe_folder = os.path.dirname(str(os.path.abspath(sys.argv[0])))
    date_prefix = datetime.today().strftime("%Y%m%d")
    out_path = os.path.join(exe_folder, 'out', common_module.remove_invalid_paths(source_id),'Skip Rules',common_module.remove_invalid_paths(location_id),date_prefix)
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    index = 1
    outFileName = os.path.join(out_path, common_module.remove_invalid_paths(rule_name) + extention)
    retFileName = outFileName
    while os.path.isfile(retFileName):
        retFileName = os.path.join(out_path, common_module.remove_invalid_paths(rule_name)+"_"+str(index) + extention)
        index +=1
    return retFileName

# 1. File Reading
# Read allowed rules from the file
allowed_rules = []
ignore_rules = []

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('skip.txt')


# Remove any newline characters from each line and clean the string
allowed_rules = [rule.strip().replace('â€ƒ', ' ').replace('â€‰', ' ') for rule in allowed_rules]

sheet_links = {
    'Arizona Rules of Professional Conduct': 'https://tools.azbar.org/RulesofProfessionalConduct/RulesofProfessionalConduct.aspx?',
    'Rules of the Supreme Court of Arizona': 'https://govt.westlaw.com/azrules/Browse/Home/Arizona/ArizonaCourtRules/ArizonaStatutesCourtRules?guid=N96EE7620715511DAA16E8D4AC7636430&transitionType=CategoryPageItem&contextData=(sc.Default)',
    'Rules of Civil Procedure for the Superior Courts of Arizona': 'https://govt.westlaw.com/azrules/Browse/Home/Arizona/ArizonaCourtRules/ArizonaStatutesCourtRules?guid=N93E3A75086BD11E6B9D68CD8AD30786D&transitionType=CategoryPageItem&contextData=(sc.Default)&bhcp=1',
    'Arizona Rules of Civil Appellate Procedure': 'https://govt.westlaw.com/azrules/Browse/Home/Arizona/ArizonaCourtRules/ArizonaStatutesCourtRules?guid=N0854C3F0715611DAA16E8D4AC7636430&transitionType=CategoryPageItem&contextData=(sc.Default)',
    'Rules of Criminal Procedure': 'https://govt.westlaw.com/azrules/Browse/Home/Arizona/ArizonaCourtRules/ArizonaStatutesCourtRules?guid=NCB1EB43070CB11DAA16E8D4AC7636430&transitionType=CategoryPageItem&contextData=(sc.Default)',
    'Rules of Evidence for Courts in the State of Arizona': 'https://govt.westlaw.com/azrules/Browse/Home/Arizona/ArizonaCourtRules/ArizonaStatutesCourtRules?guid=N89B7E4A0715511DAA16E8D4AC7636430&transitionType=CategoryPageItem&contextData=(sc.Default)'
}

# 2. Web Scraping
# Fetch the content from the URL
errors =[]

for rule_name, url in sheet_links.items():
    try:
        if rule_name not in ('Arizona Rules of Professional Conduct', 'Rules of Criminal Procedure'):
            response = requests.get(url)
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            all_links = soup.find('ul', class_='co_genericWhiteBox').find_all('a')

            # 3. Comparison Logic
            # Initialize list to keep track of matching rules
            matching_rules = []
            skip_rules = []
            # Iterate through all links and check if the link text exists in the allowed_rules list
            for link in all_links:
                text = link.text.strip().replace('â€ƒ', ' ').replace('â€‰',' ')
                if(link in ignore_rules):
                    continue
                href = 'https://govt.westlaw.com' + link.get('href')
                # Check if the text exists in allowed_rules
                if text in allowed_rules:
                    print(f"Matching rule found: {text}")
                    print(f"Link: {href}")
                    matching_rules.append((text, href))
                else:
                    skip_rules.append(text)
                    matching_rules.append((text, href))

            print(skip_rules)
            non_match_rulz = []
            # 4. Web Scraping Inside Matching Links
            for rule_text, link_url in matching_rules:
                try:
                    response_inside = requests.get(link_url)
                    soup_inside = BeautifulSoup(response_inside.content, 'html.parser')

                    # Extract the content inside the matching link
                    content_elements = soup_inside.find('ul', class_='co_genericWhiteBox').find_all('a')

                    if content_elements:
                        for element in content_elements:
                            try :
                                href = 'https://govt.westlaw.com' + element.get('href')
                                encoded_url = urllib.parse.quote(href, safe=":/?=&")
                                cur_rule_text = element.get_text()
                                print(cur_rule_text)
                                if not cur_rule_text in allowed_rules:
                                    skip_rules.append(cur_rule_text)
                                    response = requests.get(encoded_url)
                                    soup = BeautifulSoup(response.content, 'html.parser')
                                    rule_ele = soup.find('div', class_='co_genericWhiteBox')
                                    deleteEle1 = rule_ele.find("div", {"id": "navBar"})
                                    if deleteEle1:
                                        deleteEle1.replaceWith('')
                                    deleteEle2 = rule_ele.find("table", {"id": "co_endOfDocument"})
                                    if deleteEle2:
                                        deleteEle2.replaceWith('')

                                    output_fileName = skip_rule_file(source_id, rule_name, cur_rule_text, '.html')

                                    with open(output_fileName, 'w', encoding='utf-8') as f:
                                        f.write(str(rule_ele))

                                else:
                                    print(f"Matching rule found: {cur_rule_text}")
                                    # Save each content element as a separate text file
                                    response = requests.get(encoded_url)
                                    soup = BeautifulSoup(response.content, 'html.parser')
                                    rule_ele = soup.find('div', class_='co_genericWhiteBox')
                                    deleteEle1 = rule_ele.find("div", {"id": "navBar"})
                                    if deleteEle1:
                                        deleteEle1.replaceWith('')
                                    deleteEle2 = rule_ele.find("table", {"id": "co_endOfDocument"})
                                    if deleteEle2:
                                        deleteEle2.replaceWith('')

                                    output_fileName = common_module.ret_file_name_full(source_id, rule_name, cur_rule_text, '.html')
                                    print(output_fileName)
                                    print(rule_ele)


                                    with open(output_fileName, 'w', encoding='utf-8') as f:
                                        f.write(str(rule_ele))
                            except Exception as element_error:
                                print(element_error)
                                errors.append(element_error)

                    else:
                        print(f"No content found for {rule_text}")
                except requests.RequestException as matching_rules_errors:
                    print(f"Failed to fetch content from {link_url}: {matching_rules_errors}")
                    errors.append(matching_rules_errors)
        elif rule_name in 'Rules of Criminal Procedure':
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            all_links = soup.find('ul', class_='co_genericWhiteBox').find_all('a')

            matching_rules = []
            skip_rules: list[str] = []
            print(skip_rules)
            non_match_rulz = []

            for link in all_links:
                text = link.text.strip().replace('â€ƒ', ' ').replace('â€‰',' ')  # Remove any extra whitespace and clean
                href = 'https://govt.westlaw.com' + link.get('href')
                # Check if the text exists in allowed_rules
                if text in allowed_rules:
                    matching_rules.append((text, href))
                else:
                    skip_rules.append(text)

            for rule_text, link_url in matching_rules:
                try:
                    response_inside = requests.get(link_url)
                    soup_inside = BeautifulSoup(response_inside.content, 'html.parser')
                    content_elements = soup_inside.find('ul', class_='co_genericWhiteBox').find_all('a')

                    for element in content_elements:
                        try:
                            href = 'https://govt.westlaw.com' + element.get('href')
                            encoded_url = urllib.parse.quote(href, safe=":/?=&")
                            cur_rule_text = element.get_text()
                            if not cur_rule_text in allowed_rules:
                                skip_rules.append(cur_rule_text)
                            else:
                                response = requests.get(encoded_url)
                                soup_rule = BeautifulSoup(response.content, 'html.parser')
                                next_rule = soup_rule.find('ul', class_='co_genericWhiteBox').find_all('a')
                                print(next_rule)
                                for element_rule in next_rule:
                                    element_href = 'https://govt.westlaw.com' + element_rule.get('href')
                                    element_encode_url = urllib.parse.quote(element_href, safe=":/?=&")
                                    element_text = element_rule.get_text()
                                    if element_text not in allowed_rules:
                                        print(f"Matching rule found: {element_text}")
                                        # Save each content element as a separate text file                                        response = requests.get(element_encode_url)
                                        soup_element = BeautifulSoup(response.content, 'html.parser')
                                        rule_ele = soup_element.find('div', class_='co_genericWhiteBox')
                                        deleteEle1 = rule_ele.find("div", {"id": "navBar"})
                                        if deleteEle1:
                                            deleteEle1.replaceWith('')
                                        deleteEle2 = rule_ele.find("table", {"id": "co_endOfDocument"})
                                        if deleteEle2:
                                            deleteEle2.replaceWith('')
                                        print(rule_ele)

                                        output_fileName = common_module.ret_file_name_full(source_id, rule_name, element_text,'.html')

                                        with open(output_fileName, 'w', encoding='utf-8') as f:
                                            f.write(str(rule_ele))
                        except Exception as element_error:
                            print(element_error)


                except requests.RequestException as matching_rules_errors:
                    print(f"Failed to fetch content from {link_url}: {matching_rules_errors}")
        else:
            response = requests.get(url)

            soup = BeautifulSoup(response.content, 'html.parser')
            # Check if the div element with the specified class exists
            element_by_id = soup.find("div", {"id": "sectionsAccordion"}).find_all('h3', recursive=False)

            skip_rules = []
            print(skip_rules)
            for link in element_by_id:
                text = link.text.strip()
                if text in allowed_rules:
                    next_siblings = link.find_next_sibling("div").find("div", id='rulesAccordion').find_all('h3',recursive=False)
                    print(next_siblings)
                    for next_sibling in next_siblings:
                        next_sibling_text = next_sibling.get_text(strip=True)
                        if next_sibling_text in allowed_rules:
                            Current_Rule = next_sibling.find_next_sibling("div").find('a', class_='btn btn-default')
                            print(Current_Rule)
                            href = "https://tools.azbar.org/RulesofProfessionalConduct/" + Current_Rule.get('href')
                            response_1 = requests.get(href)
                            soup_ = BeautifulSoup(response_1.content, 'html.parser')
                            get_all_text = soup_.find('form')
                            print(get_all_text)
                            deleteEle1 = get_all_text.find("input", {"id": "__VIEWSTATE"})
                            if deleteEle1:
                                deleteEle1.replaceWith('')
                            deleteEle2 = get_all_text.find("input", {"id": "__VIEWSTATEGENERATOR"})
                            if deleteEle2:
                                deleteEle2.replaceWith('')
                            deleteEle3 = get_all_text.find("a", {"id": "MyHeader_rule_Repeater_Opinions_Link_0"})
                            if deleteEle3:
                                deleteEle3.replaceWith('')

                            output_fileName = common_module.ret_file_name_full(source_id, rule_name, next_sibling_text, '.html')
                            print(get_all_text)
                            with open(output_fileName, 'w', encoding='utf-8') as f:
                                f.write(str(get_all_text))


                        else:
                            skip_rules.append(next_sibling_text)
                            Current_Rule = next_sibling.find_next_sibling("div").find('a', class_='btn btn-default')
                            href = "https://tools.azbar.org/RulesofProfessionalConduct/" + Current_Rule.get('href')
                            response_1 = requests.get(href)
                            soup_ = BeautifulSoup(response_1.content, 'html.parser')
                            get_all_text = soup_.find('form')
                            print(get_all_text)
                            deleteEle1 = get_all_text.find("input", {"id": "__VIEWSTATE"})
                            if deleteEle1:
                                deleteEle1.replaceWith('')
                            deleteEle2 = get_all_text.find("input", {"id": "__VIEWSTATEGENERATOR"})
                            if deleteEle2:
                                deleteEle2.replaceWith('')
                            deleteEle3 = get_all_text.find("a", {"id": "MyHeader_rule_Repeater_Opinions_Link_0"})
                            if deleteEle3:
                                deleteEle3.replaceWith('')

                            output_fileName = skip_rule_file(source_id, rule_name, next_sibling_text, '.html')
                            with open(output_fileName, 'w', encoding='utf-8') as f:
                                f.write(str(get_all_text))

                else:
                    skip_rules.append(text)
    except Exception as sheet_links_error:
        errors.append(sheet_links_error)

