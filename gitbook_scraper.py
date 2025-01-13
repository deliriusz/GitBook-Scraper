import sys
import requests
from bs4 import BeautifulSoup
import html2text
import urllib.parse
from selenium import webdriver
import time

def fetch_html(url):
    # TODO: change path
    # alternatively, webdriver_manager could be used: https://github.com/SergeyPirogov/webdriver_manager
    service = webdriver.FirefoxService(executable_path='/snap/bin/firefox.geckodriver')
    options = webdriver.FirefoxOptions()
    options.page_load_strategy = 'eager'

    options.add_argument('-headless')
    assert options.capabilities['browserName'] == 'firefox'
    driver = webdriver.Firefox(options=options,service=service)
    driver.get(url)

    source = driver.page_source
    driver.quit()
    return source

def extract_content_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Debug: print out the HTML to inspect the structure
    # print(soup.prettify())  # Uncomment this line if you want to see the raw HTML output

    # Adjust the selector based on the actual GitBook structure
    content = soup.find('main')  # Update this selector based on inspection
    if content is None:
        raise ValueError("Failed to find content area in the HTML.")
    
    return str(content)

def convert_html_to_markdown(html_content):
    h = html2text.HTML2Text()
    h.ignore_links = False
    markdown_content = h.handle(html_content)
    return markdown_content

def extract_page_links(soup, base_url):
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        href_no_local_tag = href.split('#')[0]
        full_url = urllib.parse.urljoin(base_url, href_no_local_tag)
        
        # Check if the URL belongs to the same domain
        if urllib.parse.urlparse(full_url).netloc == urllib.parse.urlparse(base_url).netloc:
            links.add(full_url)
    return list(links)

def save_markdown_to_file(markdown_content, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

def main(gitbook_url, output_file):
    print(f"Fetching main page HTML content from {gitbook_url}...")
    main_page_html = fetch_html(gitbook_url)
    
    print("Extracting page links...")
    main_soup = BeautifulSoup(main_page_html, 'html.parser')
    page_links = extract_page_links(main_soup, gitbook_url)
    
    markdown_content = ""
    for link in page_links:
        print(f"Fetching content from {link}...")
        page_html = fetch_html(link)
        print("Extracting content...")
        try:
            content_html = extract_content_from_html(page_html)
            print("Converting HTML to Markdown...")
            markdown_content += convert_html_to_markdown(content_html)
            markdown_content += "\n\n"  # Add some separation between pages
        except ValueError as e:
            print(f"Error processing {link}: {e}")
    
    print(f"Saving Markdown content to {output_file}...")
    save_markdown_to_file(markdown_content, output_file)
    
    print("Done!")

if __name__ == '__main__':
    gitbook_url = sys.argv[1] # Documentation url
    output_file = 'documentation.md'  # Desired output markdown file

    main(gitbook_url, output_file)
