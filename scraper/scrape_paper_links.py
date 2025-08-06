import csv
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urljoin
from tqdm import tqdm

BASE_URL = "https://papers.nips.cc"


def extract_proceeding_links(filepath="./data/neurips_proceedings_links.csv"):
    """Reads proceeding links from CSV and pairs them with years."""
    with open(filepath, "r") as csv_file:
        csv_reader = csv.reader(csv_file)

        # Each row is a list of single link, so we need to extract the value using row[0]
        links = [row[0] for row in csv_reader]

    years = list(range(2024, 1986, -1))  # descending from 2024 to 1987
    year_data = [
        {
            "year": year, 
            "proceeding_link": link, 
            "paper_links": []
        }
        
        for year, link in zip(years, links[1:])  # skip header
    ]

    return year_data


def collect_paper_links(year_data_list):
    """Populates each year's dict with its corresponding paper links."""
    for year_data in tqdm(year_data_list):
        try:
            url = year_data["proceeding_link"]
            page = urlopen(url)
            soup = BeautifulSoup(page.read().decode("utf-8"), "html.parser")

            ul = soup.find("ul", class_="paper-list")
            if ul:
                paper_links = [
                    urljoin(BASE_URL, a_tag["href"])
                    for a_tag in ul.find_all("a", href=True)
                ]
                year_data["paper_links"] = paper_links

        except Exception as e:
            print(f"Failed to process {year_data['year']} - {url}: {e}")

    return year_data_list


def save_papers_to_csv(year_data_list, out_path="./data/neurips_papers.csv"):
    """
    Write one row per paper link, with columns:
    year, proceeding_link, paper_link
    """
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["year", "proceeding_link", "paper_link"])
        for data in year_data_list:
            year = data["year"]
            proc = data["proceeding_link"]
            for paper_link in data["paper_links"]:
                writer.writerow([year, proc, paper_link])

    print(f"Saved {out_path}")


if __name__ == "__main__":
    year_data_list = extract_proceeding_links()
    results = collect_paper_links(year_data_list)
    save_papers_to_csv(results)
