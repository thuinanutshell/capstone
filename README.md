# NeurIPIS Dataset (1987-2024)
This project is developed out of curiosity. I'm curious about the number of papers accepted into NeurIPS over time and the most prominent topics each year. I will use `beautifulsoup` to scrape the abstract of all papers and implement some analyses like topic modeling or clustering to explore what's interesting about the data.

## Web Scraper Tutorial
### Step 1: Inspect & Collect Proceedings Links
**Inspect** the main webpage and define the links or the elements that need to be extracted. 

Below is the main page of the NeurIPS Proceedings (https://papers.nips.cc/), which consists of links to all the papers and their abstract in a specific year. As a result, we first need to collect all these links so that we can visit each of them and extract the data from there.

<img src="./neurips_main.png">

Notice that the list of all the proceeding links are within the element `div` with the class name `col-sm p-3`. Therefore, we need to first find this `div`. After that, we will find all the `li` elements within it and the `a` element inside the `li` element. 

Then, extract the `href` attribute from the `a` tag. The link to each year's proceedings is the **joined URL** between the base URL (https://papers.nips.cc/) and the `href` value. For example: https://papers.nips.cc/paper_files/paper/2024

### Step 2: Open Each Proceeding Link & Collect Paper Links

### Step 3: Open Each Paper Link & Collect Abstract

## Data Analysis
## Resources
[1] https://realpython.com/python-web-scraping-practical-introduction/