from selenium import webdriver
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
import logging
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from progress_bar import Progress


class Scraper:
    def __init__(self):
        self.scrapped_data_path = "./Scrapped_Data"
        self.separator = "###SEPARATOR###"
        self.input_data = pd.read_excel('Input.xlsx')
        self.make_directory(self.scrapped_data_path)

    def run_scraper(self):
        """
        Runs the web scraper for each URL in the input data and displays a progress bar.
        """
        total_urls = len(self.input_data)
        pbar = Progress(total_iterations=total_urls)
        pbar.start()
        for i in range(total_urls):
            url_id, url = self.input_data.iloc[i, 0], self.input_data.iloc[i, 1]
            heading, text = self.scrape_article(url=url)
            self.absentee_check(url_id, url, heading, text)
            self.save_txt(name=url_id, content=f"heading:{heading}\n{self.separator}\ntext:{text}",
                            path=self.scrapped_data_path)
            pbar.update(1)

    def scrape_article(self, url):
        """
        Scrapes the web page at the given URL to extract the heading and text.
        """
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        unwanted_tags = soup.select("script, style")
        for tag in unwanted_tags:
            tag.extract()

        heading = ""
        try:
            heading = soup.select_one("[class*='td-parallax-header'] h1").get_text()
        except AttributeError:
            pass

        try:
            heading = soup.select_one("[class*='tdb_title'] h1").get_text()
        except AttributeError:
            pass

        article = ""
        try:
            articles = soup.select("[class*='td-post-content'] p")
            article = '\n\n'.join([p.get_text() for p in articles])
        except AttributeError:
            pass

        return heading, article

    def save_txt(self, name, content, path):
        """
        Saves the scraped content to a text file.
        """
        with open(os.path.join(path, f"{name}.txt"), 'w', encoding='utf-8') as file:
            file.write(content)

    def absentee_check(self, url_id, url, heading, text):
        """
        Checks if the heading and/or text are missing and updates the "absentee" Excel file accordingly.
        """
        if not heading and not text:
            if not os.path.exists("absentee.xlsx"):
                data = pd.DataFrame(columns=["url_id", "url", "heading", "text"])
                data.to_excel("absentee.xlsx")
            data = pd.read_excel("absentee.xlsx").drop('Unnamed: 0', axis=1)
            new_row = pd.Series([url_id, url, 0, 0], index=data.columns)
            data = pd.concat([data, new_row.to_frame().transpose()], ignore_index=True)
            data.to_excel("absentee.xlsx")

        elif not text:
            if not os.path.exists("absentee.xlsx"):
                data = pd.DataFrame(columns=["url_id", "url", "heading", "text"])
                data.to_excel("absentee.xlsx")
            data = pd.read_excel("absentee.xlsx").drop('Unnamed: 0', axis=1)
            new_row = pd.Series([url_id, url, 1, 0], index=data.columns)
            data = pd.concat([data, new_row.to_frame().transpose()], ignore_index=True)
            data.to_excel("absentee.xlsx")

    def make_directory(self, directory):
        """
        Creates the directory if it doesn't exist.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)


if __name__ == '__main__':
    scraper = Scraper()
    scraper.run_scraper()
