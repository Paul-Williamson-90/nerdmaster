from typing import List
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import warnings as warning
from tqdm import tqdm
import time
import random
import os


class BasicScraperException(Exception):
    pass

class BasicScraperWarning(Warning):
    pass

class BasicScraper:

    def __init__(self, 
                 root_page:str="https://api.python.langchain.com/en/latest/langchain_api_reference.html", 
                 parent_root:str="https://api.python.langchain.com/en/latest/",
                 documentation_save_path:Path=Path("./scraped_documentation"),
                 wait_time_max:int=3,
                 maximum_pages:int=1000,
                 ):
        """
        Initialize the BasicScraper object.
        This class is used to scrape documentation from a website.

        Parameters:
        root_page (str): The root page to start scraping from.
        parent_root (str): The parent root of the root page.
        documentation_save_path (Path): The path to save the scraped documentation.
        wait_time_max (int): The maximum wait time between requests.
        maximum_pages (int): The maximum number of pages to scrape.

        Methods:
        scrape: Perform the scraping operation.
        """
        self.root_page: str = root_page
        self.parent_root: str = parent_root
        self.documentation_save_path: Path = documentation_save_path
        self.urls_to_visit: List[str] = [root_page]
        self.urls_visited: List[str] = []
        self.bad_urls: List[str] = []
        self.wait_time_max: int = wait_time_max
        self.maximum_pages: int = maximum_pages
        self._create_save_path()
        self._clean_save_path()

    def _clean_save_path(self):
        for file in os.listdir(self.documentation_save_path):
            os.remove(Path(f"{self.documentation_save_path}/{file}"))

    def _create_save_path(self):
        if not os.path.exists(self.documentation_save_path):
            os.makedirs(self.documentation_save_path)

    def _create_wait_time(self):
        return random.randint(0, self.wait_time_max)
    
    def _wait(self):
        if self.wait_time_max > 0:
            time.sleep(self._create_wait_time())

    def _get_soup(self, url):
        page = requests.get(url)
        status_code = page.status_code
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup, status_code

    def _get_page_content(self, soup):
        content = soup.get_text()
        return content

    def _get_page_title(self, soup):
        title = soup.title.string
        return title

    def _save_content(self, content, title):
        with open(Path(f"{self.documentation_save_path}/{title}.txt"), "w") as file:
            file.write(content)
            file.close()

    def _get_page_urls(self, soup):
        links = soup.select('a')
        urls = [link['href'] for link in links]
        return urls

    def _filter_urls(self, urls):
        filtered = []
        for url in urls:
            if url not in self.urls_visited:
                filtered.append(url)
        return filtered

    def _add_to_urls_to_visit(self, urls):
        for url in urls:
            self.urls_to_visit.append(url)

    def _add_to_urls_visited(self, url):
        self.urls_visited.append(url)

    def _concat_urls(self, urls):
        return [f"{self.parent_root}{url}" if "http" not in url else url for url in urls]

    def _visit_url(self, url):
        attempts = 0
        while True:
            try:
                soup, status_code = self._get_soup(url)
                if status_code != 200:
                    if status_code == 404:
                        self._add_bad_url(url)
                        warning.warn(str(f"Failed to visit {url}:\n{e}"), BasicScraperWarning)
                        break
                    raise BasicScraperException(f"Failed to visit {url} with status code {status_code}.")
                content = self._get_page_content(soup)
                title = self._get_page_title(soup)
                self._save_content(content, title)
                urls = self._get_page_urls(soup)
                concat_urls = self._concat_urls(urls)
                filtered_urls = self._filter_urls(concat_urls)
                self._add_to_urls_to_visit(filtered_urls)
                self._add_to_urls_visited(url)
                break
            except Exception as e:
                warning.warn(str(f"Failed to visit {url}:\n{e}"), BasicScraperWarning)
                attempts += 1
                self._wait()
                if attempts > 3:
                    warning.warn(str(f"Failed to visit {url} after 3 attempts.\n{e}"), BasicScraperWarning)
                    self._add_bad_url(url)
                    break

    def _add_bad_url(self, url):
        self.bad_urls.append(url)

    def _report(self):
        print("Scraping complete.")
        print(f"Number of urls visited: {len(self.urls_visited)}")
        print(f"Number of bad urls: {len(self.bad_urls)}")

    def _check_maximum_pages(self):
        if self.maximum_pages:
            if len(self.urls_visited) >= self.maximum_pages:
                return True
        return False

    def scrape(self):
        """
        Perform the scraping operation.
        Iterate through the urls to visit and scrape the content.
        More urls are added to the urls to visit as the scraping progresses.
        """
        progress_bar = tqdm(total=len(self.urls_to_visit), position=0, leave=True)
        while len(self.urls_to_visit) > 0:
            if self._check_maximum_pages():
                break
            url = self.urls_to_visit.pop(0)
            self._visit_url(url)
            progress_bar.update(1)
            progress_bar.total = min([len(self.urls_to_visit), self.maximum_pages])
            self._wait()
        progress_bar.close()
        self._report()
        