import pandas as pd
import spacy
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from tqdm import tqdm

# Load data
df = pd.read_csv("./data/neurips_abstract_2024.csv")

# Load spaCy and set max length
nlp = spacy.load("en_core_web_sm")
nlp.max_length = 10_000_000

# Preprocess with spaCy pipe
tokens = []
for doc in tqdm(
    nlp.pipe(df["abstract"].astype(str).str.lower(), batch_size=50), total=len(df)
):
    tokens.extend(
        [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    )

# Custom stopwords
custom_stopwords = {
    "model",
    "data",
    "dataset",
    "task",
    "method",
    "approach",
    "result",
    "paper",
    "experiment",
    "experiments",
    "propose",
    "proposed",
    "show",
    "demonstrate",
    "performance",
    "achieve",
    "based",
    "using",
    "provide",
    "use",
    "base",
    "datum",
    "learn",
    "training",
    "state",
    "art",
    "exist",
    "include",
    "novel",
    "different",
    "improve",
    "present",
    "allow",
    "introduce",
    "design",
    "framework",
    "setting",
    "evaluation",
    "evaluate",
    "consider",
    "multiple",
    "available",
    "require",
    "utilize",
    "analysis",
    "find",
    "effectively",
    "general",
    "specifically",
    "current",
    "work",
    "term",
    "obtain",
    "leverage",
    "help",
    "capability",
    "need",
    "example",
    "identify",
    "lead",
    "notion",
    "give",
    "incorporate",
    "furthermore",
    "prove",
    "solution",
    "study",
    "well",
    "problem",
    "enable",
    "specific",
    "high",
    "explore",
    "employ",
    "address",
    "enhance",
    "directly",
    "involve",
    "type",
    "previous",
    "new",
    "technique",
    "establish",
    "produce",
    "non",
    "offer",
    "recent",
    "develop",
    "apply",
    "typically",
    "support",
    "aim",
    "despite",
    "additionally",
    "significantly",
    "extensive",
    "recently",
    "feature",
    "challenge",
    "sample",
    "train",
    "information",
    "finally",
    "make",
    "rely",
    "perform",
    "exhibit",
    "pre",
    "machine learning",
    "reveal",
}

# Apply stopword filtering
tokens = [word for word in tokens if word not in custom_stopwords]

# Generate word cloud
text = " ".join(tokens)
wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)

# Display
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.title("Word Cloud for Abstracts")
plt.show()
