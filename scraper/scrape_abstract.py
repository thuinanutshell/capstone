import csv
from bs4 import BeautifulSoup
from urllib.request import urlopen
from tqdm import tqdm


def extract_paper_links(filepath="./data/neurips_papers.csv", target_year=None):
    """Reads paper links from CSV"""
    paper_data = []

    with open(filepath, "r", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # skip header

        for row in csv_reader:
            if target_year:
                if row[0] == target_year:
                    paper_data.append(
                        {
                            "year": row[0],
                            "proceeding_link": row[1],
                            "paper_link": row[2],
                        }
                    )
            else:
                paper_data.append(
                    {"year": row[0], "proceeding_link": row[1], "paper_link": row[2]}
                )

    return paper_data


def collect_abstract(paper_data):
    all_data = []

    for paper in tqdm(paper_data):
        try:
            url = paper["paper_link"]
            page = urlopen(url)
            soup = BeautifulSoup(page.read().decode("utf-8"), "html.parser")

            div = soup.find("div", class_="col p-3")
            paper_result = {
                "year": paper["year"],
                "proceeding_link": paper["proceeding_link"],
                "paper_link": paper["paper_link"],
            }

            if div:
                h4_tags = div.find_all("h4")
                # Title = first h4
                paper_result["title"] = (
                    h4_tags[0].text.strip() if len(h4_tags) > 0 else ""
                )

                # Authors = content of <p><i> immediately after <h4>Authors</h4>
                authors_tag = div.find("h4", string="Authors")
                if authors_tag:
                    authors_p = authors_tag.find_next_sibling("p")
                    authors_i = authors_p.find("i") if authors_p else None
                    paper_result["authors"] = (
                        authors_i.text.strip() if authors_i else ""
                    )
                else:
                    paper_result["authors"] = ""

                # Abstract = all <p> tags after <h4>Abstract</h4>
                abstract_tag = div.find("h4", string="Abstract")
                abstract = ""
                if abstract_tag:
                    next_sibling = abstract_tag
                    while True:
                        next_sibling = next_sibling.find_next_sibling()
                        if next_sibling and next_sibling.name == "p":
                            abstract += next_sibling.text.strip() + " "
                        else:
                            break
                paper_result["abstract"] = abstract.strip()

            all_data.append(paper_result)

        except Exception as e:
            print(f"Error processing {paper['paper_link']}: {e}")
            continue

    return all_data


def save_abstract_to_csv(data, filename):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["year", "proceeding_link", "paper_link", "title", "authors", "abstract"]
        )
        for d in data:
            writer.writerow(
                [
                    d["year"],
                    d["proceeding_link"],
                    d["paper_link"],
                    d["title"],
                    d["authors"],
                    d["abstract"],
                ]
            )


if __name__ == "__main__":
    for year in tqdm(range(2023, 1986, -1)):
        paper_links = extract_paper_links(target_year=str(year))
        results = collect_abstract(paper_links)
        save_abstract_to_csv(results, filename=f"./data/neurips_abstract_{year}.csv")