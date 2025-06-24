# NeurIPS Research Analysis
This is a project developed out of curiosity about the research trends in AI and Machine Learning over the past 40 years. I scraped all 38 proceedings' research papers and their abstracts and employed some data analysis techniques, such as topic modeling and k-means clustering, to visualize semantically similar papers. Through this project, I want to answer the following questions:
- How has the landscape of AI/ML research changed over the past few years?
- What are some of the papers that stand the test of time or are being cited the most?
- Can we somehow predict what areas/topics of research are worth pursuing now or in the near future based on past data?

# Dataset
The papers and their abstracts are scraped from the NeurIPS Website: https://papers.nips.cc/ using `BeautifulSoup`. There are a total of **24,000+** papers. I have just scraped the 2024 proceeding with about 4500 papers, and it took ~4 hours, so we should expect the whole process to take about 20 hours to scrape all the papers.

# Initial Results
## K-Means Clustering of 10 Topics
<img width="856" alt="Screenshot 2025-06-24 at 10 18 20 AM" src="https://github.com/user-attachments/assets/7ddd0603-fd39-41fe-a3ae-964a75456f8c" />
