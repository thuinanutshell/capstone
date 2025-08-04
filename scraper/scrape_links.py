from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urljoin
import csv

base_url = "https://papers.nips.cc/"

def collect_proceeding_links(base_url):
    page = urlopen(base_url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    
    div = soup.find("div", class_="col-sm p-3")
    links = []
    
    if div:
        items = div.find_all("li")
        for item in items:
            a_tag = item.find("a")
            if a_tag and a_tag.has_attr("href"):
                full_link = urljoin(base_url, a_tag["href"])
                links.append(full_link)
    return links

def save_links_to_csv(links, filename="./data/neurips_proceedings_links.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Link"])
        for link in links:
            writer.writerow([link])
    
if __name__ == "__main__":
    proceeding_links = collect_proceeding_links(base_url)
    save_links_to_csv(proceeding_links)