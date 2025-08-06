import pandas as pd
import matplotlib.pyplot as plt


def get_paper_counts():
    df = pd.read_csv("./data/neurips_papers.csv")
    counts = df["year"].value_counts().sort_index(ascending=False)
    return counts.to_dict()


data = get_paper_counts()
years = list(data.keys())
counts = list(data.values())

plt.figure(figsize=(12,6))
plt.bar(years, counts)
plt.xlabel("Year")
plt.ylabel("Number of Papers")
plt.title("Number of NeurIPS Papers Per Year")
plt.xticks(years, rotation=45)
plt.tight_layout()
plt.show()
