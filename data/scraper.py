from urllib.request import urlopen
from bs4 import BeautifulSoup
import re


class WebScraper:
    """Logic to extract information from all papers from NeurIPS

    1. A function to collect all the URLs of the NeurIPS Proceedings (each year)
    2. A function that follows each of the Proceeding URL and collects all the paper links for that proceeding
    3. A function that follows each paper link to extract information: Title, Authors, Abstract
    """

    def __init__(self, source_url):
        self.source_url = source_url

    def collect_hrefs(self, elem, pattern, url=None):
        """Helper function to collect all links matching a pattern"""
        target_url = url if url else self.source_url
        page = urlopen(target_url)
        html = page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for link in soup.find_all(elem, href=re.compile(pattern)):
            links.append(target_url + link["href"])
        return links

    def collect_proceedings(self):
        """Collect all proceedings URLs"""
        return self.collect_hrefs("a", "/paper_files/paper/")

    def collect_papers(self, proceedings):
        """Collect paper links from each proceeding"""
        paper_dict = {proceeding: [] for proceeding in proceedings}
        for proc_url in paper_dict:
            page = urlopen(proc_url)
            html = page.read().decode("utf-8")
            soup = BeautifulSoup(html, "html.parser")

            # Find the paper list container
            paper_list = soup.find("ul", class_="paper-list")
            if paper_list:
                # Find all paper links within the list
                for link in paper_list.find_all("a", href=True):
                    paper_dict[proc_url].append(self.source_url + link["href"])
        return paper_dict

    def collect_paper_data(self, paper_url):
        """Extract title, authors, abstract from a paper page"""
        page = urlopen(paper_url)
        html = page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        
        # Initialize default values
        title = "Unknown"
        authors = "Unknown"
        abstract = "Unknown"
        
        # Find all container-fluid divs
        containers = soup.find_all("div", class_="container-fluid")
        
        # Use the second container if available (main content container)
        if len(containers) >= 2:
            container = containers[1]
        elif containers:
            container = containers[0]
        else:
            return {"title": title, "authors": authors, "abstract": abstract}
        
        # Find the col p-3 div which contains our content
        col_div = container.find("div", class_="col p-3")
        if col_div:
            # Extract title (first h4 within col p-3)
            if col_div.find("h4"):
                title = col_div.find("h4").text.strip()
            
            # Extract authors (h4 with text "Authors" and get the following p)
            authors_h4 = col_div.find("h4", string="Authors")
            if authors_h4 and authors_h4.find_next("p"):
                authors = authors_h4.find_next("p").text.strip()
            
            # Extract abstract (h4 with text "Abstract" and get the following p elements)
            abstract_h4 = col_div.find("h4", string="Abstract")
            if abstract_h4:
                abstract_paragraphs = []
                current = abstract_h4.find_next("p")
                while current and current.name == "p":
                    # Skip empty paragraphs
                    if current.text.strip():
                        abstract_paragraphs.append(current.text.strip())
                    current = current.find_next_sibling()
                    # Stop if we hit another h4
                    if current and current.name == "h4":
                        break
                if abstract_paragraphs:
                    abstract = " ".join(abstract_paragraphs)
        
        return {
            "title": title,
            "authors": authors,
            "abstract": abstract
        }
