import time
import csv
import random
from pathlib import Path
from scraper import WebScraper
from urllib.request import urlopen
from bs4 import BeautifulSoup

def test_single_proceeding():
    source_url = "https://papers.nips.cc/"
    scraper = WebScraper(source_url)
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 1. Collect proceedings
    print("Collecting proceedings...")
    proceedings = scraper.collect_proceedings()
    print(f"Found {len(proceedings)} proceedings")
    
    if not proceedings:
        print("No proceedings found. Exiting.")
        return
    
    # 2. Select the first proceeding for testing
    test_proceeding = proceedings[0]
    print(f"Testing with proceeding: {test_proceeding}")
    
    # 3. Collect papers from the selected proceeding
    papers_dict = {test_proceeding: []}
    print("Collecting paper links...")
    
    # Use the collect_papers method but with just one proceeding
    full_papers_dict = scraper.collect_papers([test_proceeding])
    papers_dict[test_proceeding] = full_papers_dict[test_proceeding]
    
    paper_urls = papers_dict[test_proceeding]
    print(f"Found {len(paper_urls)} papers in the proceeding")
    
    # 4. Limit to first paper for debugging
    test_paper_url = paper_urls[0]
    print(f"Testing with first paper: {test_paper_url}")
    
    # 5. Print HTML source for debugging
    try:
        print(f"Fetching HTML for: {test_paper_url}")
        page = urlopen(test_paper_url)
        html = page.read().decode("utf-8")
        
        # Save HTML to file for inspection
        html_file = output_dir / "paper_source.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML source saved to {html_file}")
        
        # Parse with BeautifulSoup and print structure
        soup = BeautifulSoup(html, "html.parser")
        
        # Find all container-fluid divs
        containers = soup.find_all("div", class_="container-fluid")
        print(f"\nFound {len(containers)} container-fluid divs")
        
        # Process the second container if available
        if len(containers) >= 2:
            container = containers[1]  # Use the second container
            print("Using the second container-fluid div")
        elif containers:
            container = containers[0]  # Use the first container if only one exists
            print("Using the first container-fluid div")
        else:
            print("No container-fluid div found")
            return
            
        # Find col p-3 div
        col_div = container.find("div", class_="col p-3")
        if col_div:
            print("Found col p-3 div")
            
            # Find all h4 tags in the col div
            h4_tags = col_div.find_all("h4")
            print(f"Found {len(h4_tags)} h4 tags in col p-3:")
            for i, h4 in enumerate(h4_tags):
                print(f"  h4 #{i+1}: {h4.text.strip()}")
        else:
            print("No col p-3 div found")
        
        # Find all h4 tags anywhere in container
        all_h4_tags = container.find_all("h4")
        print(f"\nFound {len(all_h4_tags)} h4 tags anywhere in container:")
        for i, h4 in enumerate(all_h4_tags):
            print(f"  h4 #{i+1}: {h4.text.strip()}")
            # Print parent element
            parent = h4.parent
            print(f"    Parent: {parent.name} class={parent.get('class', 'None')}")
        
        # Find Authors and Abstract sections
        authors_h4 = container.find("h4", string="Authors")
        if authors_h4:
            print("\nFound Authors h4")
            print(f"  Parent: {authors_h4.parent.name}")
            next_p = authors_h4.find_next("p")
            if next_p:
                print(f"  Next p: {next_p.text.strip()[:100]}...")
        else:
            print("\nNo Authors h4 found")
        
        abstract_h4 = container.find("h4", string="Abstract")
        if abstract_h4:
            print("\nFound Abstract h4")
            print(f"  Parent: {abstract_h4.parent.name}")
            next_p = abstract_h4.find_next("p")
            if next_p:
                print(f"  Next p: {next_p.text.strip()[:100]}...")
        else:
            print("\nNo Abstract h4 found")
            
    except Exception as e:
        print(f"Error analyzing HTML: {e}")

def save_to_csv(data, filepath):
    """Save data to CSV file"""
    if not data:
        return
        
    fieldnames = data[0].keys()
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Data saved to {filepath}")

def test_paper_extraction():
    """Test the paper data extraction functionality"""
    # Initialize the scraper
    source_url = "https://papers.nips.cc/"
    scraper = WebScraper(source_url)
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 1. Collect proceedings
    print("Collecting proceedings...")
    proceedings = scraper.collect_proceedings()
    
    if not proceedings:
        print("No proceedings found. Exiting.")
        return
    
    # 2. Select just the first proceeding for testing
    test_proceeding = proceedings[0]
    
    # 3. Collect papers from the selected proceeding
    full_papers_dict = scraper.collect_papers([test_proceeding])
    paper_urls = full_papers_dict[test_proceeding]
    
    if not paper_urls:
        print("No papers found. Exiting.")
        return
    
    # 4. Test with first 5 papers
    test_papers = paper_urls[:5]
    all_papers_data = []
    
    for i, paper_url in enumerate(test_papers):
        print(f"\nTesting paper {i+1}/{len(test_papers)}: {paper_url}")
        paper_data = scraper.collect_paper_data(paper_url)
        paper_data["url"] = paper_url
        all_papers_data.append(paper_data)
        
        # Print extracted data
        print(f"Title: {paper_data['title']}")
        print(f"Authors: {paper_data['authors']}")
        print(f"Abstract: {paper_data['abstract'][:100]}...")
    
    # Save test results to CSV
    save_to_csv(all_papers_data, output_dir / "test_papers.csv")
    print(f"\nSaved {len(all_papers_data)} papers to test_papers.csv")

if __name__ == "__main__":
    # test_single_proceeding()
    test_paper_extraction()
