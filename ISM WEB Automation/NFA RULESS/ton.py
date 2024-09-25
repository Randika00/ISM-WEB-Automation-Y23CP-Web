import os
import requests
from bs4 import BeautifulSoup
import common_module  # Assuming this module contains helper functions
import re

# Define source and location IDs
source_id = 'NFA RULES'
location_id = 'Manual Rules'

# Initialize lists for allowed and ignored rules
allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

# Dictionary containing links to scrape
sheet_links = {
    'General Rules': 'https://www.nfa.futures.org/rulebooksql/rules.aspx',
}

# Sanitize rule name to remove invalid characters
def sanitize_rule_name(rule_name):
    return re.sub(r'[\/:*?"<>|]', '_', rule_name)

# Function to check and process rules
def rule_check(rule_name, html_content):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)
    if cleaned_rule_name not in ignore_rules and len(cleaned_rule_name) > 0:
        if cleaned_rule_name not in allowed_rules:
            common_module.append_new_rule(source_id, cleaned_rule_title_new)
        output_file_name = common_module.ret_file_name_full(source_id, location_id, cleaned_rule_title_new, '.html')
        with open(output_file_name, 'w', encoding='utf-8') as file:
            file.write(str(html_content))
            print(output_file_name)

for rule_name, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    div_content = soup.find('div', class_='col-sm-8 ruleContent')

    if div_content:
        h4_elements = div_content.find_all('h4')  # Find all <h4> elements within the div_content

        for index, h4_element in enumerate(h4_elements, start=1):
            rule_title = h4_element.text.strip()
            sanitized_title = sanitize_rule_name(rule_title)

            p_element = h4_element.find_next('p')  # Find the next <p> element after the <h4>
            if p_element:
                # Get the HTML content of the <p> element
                html_content = str(p_element)

                # Check if HTML content length is 1 KB or more
                if len(html_content.encode('utf-8')) >= 1024:
                    try:
                        # Process the rule and save the HTML content to a file
                        rule_check(rule_title, html_content)
                        print(f"Downloaded HTML for rule '{rule_title}' at URL: {url}")
                    except Exception as e:
                        pass

    # Find all <h4> elements indicating articles from "ARTICLE I" to "ARTICLE XVIII"
    article_sections = div_content.find_all(lambda tag: tag.name == 'h4' and tag.string and re.match(r'^ARTICLE\s+(I{1,3}|IV|V|IX|X{1,3}|XIV|XV|X{0,1}VI{0,1}I{0,3}|X{0,1}I{0,3})\s*:', tag.string, re.IGNORECASE))

    for article_heading in article_sections:
        article_name = article_heading.text.strip()

        # Find next siblings until the next <h4> or end of content and concatenate content
        article_content = ''
        next_element = article_heading.find_next_sibling()
        while next_element and next_element.name != 'h4':
            article_content += str(next_element)
            next_element = next_element.find_next_sibling()

        # Save content to an HTML file
        if article_content:
            sanitized_title = sanitize_rule_name(article_name)
            output_file_name = f"{sanitized_title}.html"
            try:
                rule_check(article_name, article_content)
                print(f"Downloaded HTML for '{article_name}'")
            except Exception as e:
                pass

    # Rest of your existing code for sections, code of arbitration, financial requirements, chapters, etc.
    # Find all <h3> elements indicating sections from "Part 100 to Part 800"
    part_sections = div_content.find_all('h3', string=re.compile(r'^Part\s+(8\d\d|7\d\d|6\d\d|5\d\d|4\d\d|3\d\d|2\d\d|1\d\d|100)\.', re.IGNORECASE))

    for section in part_sections:
        section_name = section.text.strip()

        # Find next siblings until the next <h3> or end of content and concatenate content
        content = ''
        next_element = section.find_next_sibling()
        while next_element and next_element.name != 'h3':
            content += str(next_element)
            next_element = next_element.find_next_sibling()

        # Save content to an HTML file
        if content:
            sanitized_title = sanitize_rule_name(section_name)
            output_file_name = f"{sanitized_title}.html"
            try:
                rule_check(section_name, content)
                # Rename the file with the <h3> tag content
                os.rename(output_file_name, f"{sanitized_title}.html")
                print(f"Renamed HTML file to '{sanitized_title}.html'")
            except Exception as e:
                pass

    # Find the <h2> element containing 'Code of Arbitration'
    code_of_arbitration_section = div_content.find('h2', string=re.compile(r'Code of Arbitration'))

    if code_of_arbitration_section:
        # Find next siblings until the next <h2> or end of content and concatenate content
        content = ''
        next_element = code_of_arbitration_section.find_next_sibling()
        while next_element and next_element.name != 'h2':
            content += str(next_element)
            next_element = next_element.find_next_sibling()

        # Save content to an HTML file
        if content:
            sanitized_title = sanitize_rule_name('Code of Arbitration')
            output_file_name = f"{sanitized_title}.html"
            try:
                rule_check('Code of Arbitration', content)
                # Rename the file with the <h2> tag content
                os.rename(output_file_name, f"Code of Arbitration.html")
                print(f"Renamed HTML file to 'Code of Arbitration.html'")
            except Exception as e:
                pass

    # Find the <h2> element containing 'Financial Requirements'
    Financial_Requirements_section = div_content.find('h2', string=re.compile(r'Financial Requirements'))

    if Financial_Requirements_section:
        # Find next siblings until the next <h2> or end of content and concatenate content
        content = ''
        next_element = Financial_Requirements_section.find_next_sibling()
        while next_element and next_element.name != 'h2':
            content += str(next_element)
            next_element = next_element.find_next_sibling()

        # Save content to an HTML file
        if content:
            sanitized_title = sanitize_rule_name('Financial Requirements')
            output_file_name = f"{sanitized_title}.html"
            try:
                rule_check('Financial Requirements', content)
                # Rename the file with the <h2> tag content
                os.rename(output_file_name, f"Financial Requirements.html")
                print(f"Renamed HTML file to 'Financial Requirements.html'")
            except Exception as e:
                pass

    # Scraping content from "Chapter 1" to "Chapter 15"
    chapter_sections = div_content.find_all('h3', string=re.compile(r'^Chapter\s+(1[0-5]|\d)\.'))

    for chapter_heading in chapter_sections:
        chapter_name = chapter_heading.text.strip()

        # Find next siblings until the next <h3> or end of content and concatenate content
        chapter_content = ''
        next_element = chapter_heading.find_next_sibling()
        while next_element and next_element.name != 'h3':
            chapter_content += str(next_element)
            next_element = next_element.find_next_sibling()

        # Save content to an HTML file with renamed file name
        if chapter_content:
            sanitized_title = sanitize_rule_name(chapter_name)
            output_file_name = f"{sanitized_title}.html"
            try:
                rule_check(chapter_name, chapter_content)
                # Rename the file with the <h3> tag content
                os.rename(output_file_name, f"{chapter_name}.html")
                print(f"Renamed HTML file to '{chapter_name}.html'")
            except Exception as e:
                pass

