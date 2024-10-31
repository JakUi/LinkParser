import re 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import StaleElementReferenceException


class LinkParser:

    def __init__(self):
        driver_path = 'path_to_chromedriver' # Change it to your own
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument('--headless=new')
        self.driver = webdriver.Chrome(service=Service(driver_path), options=options)
        self.all_links_set = set()
        self.checked_link_list = []
        self.languages_links = [ # script doesn't add this links to sitemap
                                   "https://abc.com",
                                   "...",
                                   "https://xyz.com" 
                                   
                               ]
        self.domain_in_regexp = "https:\/\/example\.com" # change it to your own
        self.main_page = self.domain_in_regexp.replace('\\', '')

    def _get_raw_links(self):
        all_raw_links = []
        elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/')] | //link[contains(@href, '/')]")
        for element in elements:
            try:
                link = element.get_attribute('href')
                if link:
                    all_raw_links.append(link)
            except StaleElementReferenceException:
                pass
        return all_raw_links

    def _parse_link(self, link):
        regex = rf"{self.domain_in_regexp}/(?!.*(\.png|\.css|\.exe|\.svg|\.woff2|\.ico|\.webmanifest|\.jpg)).*"
        match = re.search(regex, link)
        if match:
            return match.group(0)
        else:
            return None

    def _parse_and_add_link_to_set(self):
        all_raw_links = self._get_raw_links()
        for link in all_raw_links:
            parsed_link = self._parse_link(link)
            if parsed_link:
                self.all_links_set.add(parsed_link)

    def open_link_and_parse(self, link):
        if isinstance(link, str):
            for lang_link in self.languages_links:
                if link.count(lang_link) == 0 and link not in self.checked_link_list:
                    self.driver.get(link)
                    self._get_raw_links()
                    self._parse_and_add_link_to_set()
                    self.checked_link_list.append(link)
    
    def _write_results_to_file(self):
        with open("links.txt", "w") as file:
            for link in self.all_links_set:
                file.write(link + "\n")

    def parse_all(self, page=None):
        if not page:
            page = self.main_page
        self.open_link_and_parse(page)
        try:
            while self.all_links_set - set(self.checked_link_list):  # Continue until all unique links are checked
                for link in list(self.all_links_set):  # Iterate safely over a snapshot
                    if link not in self.checked_link_list:
                        self.open_link_and_parse(link)
                        self._write_results_to_file()
            print("All checked links:", self.all_links_set)
        except Exception as e:
            print(e)
            print(self.driver.current_url)
        finally:
            with open("links.txt", "w") as file:
                for checked_link in self.checked_link_list:
                    file.write(checked_link + "\n")
            self.driver.quit()

lp = LinkParser()
lp.open_link_and_parse("https://example.com")
