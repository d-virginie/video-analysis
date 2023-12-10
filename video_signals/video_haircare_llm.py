import pickle
import pandas as pd
from keybert import KeyBERT
from collections import Counter
from transformers import pipeline
from openai import OpenAI
from sklearn.cluster import KMeans
import numpy as np

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

OPENAI_API_KEY = "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"
client = OpenAI(api_key=OPENAI_API_KEY)

dl_url = '/Users/virginieduverlie/Downloads/short_form_videos'

with open(dl_url + '/files/top_video_sentiment.pickle', 'rb') as f:
    df = pickle.load(f)

# text = str(" ".join(df['transcript'].values))
texts = list(df['transcript'])

# Get topics
print("Get Topics per video")

kw_model = KeyBERT()
keywords = [kw_model.extract_keywords(text, top_n=7) for text in texts]

with open(dl_url + '/files/transcript_keywords.pickle', 'wb') as f:
    pickle.dump(keywords, f)

with open(dl_url + '/files/transcript_keywords.pickle', 'rb') as f:
    keywords = pickle.load(f)

list_kw = [kw[0] for k_list in keywords for kw in k_list]
grouped_kw = [[kw[0] for kw in k_list] for k_list in keywords]

print(grouped_kw)
print(Counter(list_kw))

# Get zero-shot classification
print("Get zero-shot classification per video")

top_concerns = ['treatment', 'damaged', 'strong hair', 'dandruff', 'smooth', 'coloured', 'feminist',
                'self-confidence', 'busy woman', 'discrimination', 'social image', 'science', 'natural']


classifier = pipeline("zero-shot-classification",
                      model="facebook/bart-large-mnli")

dict_topics = {}

df['classification'] = ""

for index, row in df.iterrows():
    text = row['transcript']
    if not text:
        df.at[index, 'classification'] = ([],[])
    else:
        res = classifier(' '.join(text.splitlines()), top_concerns, multi_label=True)
        df.at[index, 'classification'] = (res['labels'], res['scores'])

with open(dl_url + '/files/transcript_classified.pickle', 'wb') as f:
    pickle.dump(df, f)

with open(dl_url + '/files/transcript_classified.pickle', 'rb') as f:
    df = pickle.load(f)



# with open(dl_url + '/files/transcript_embeddings.pickle', 'rb') as f:
#     df = pickle.load(f)
#
# new_df = df.copy().loc[df['ada_embedding'] != 0]
#
# matrix = np.vstack(new_df.ada_embedding.values)
# n_clusters = 8
#
# kmeans = KMeans(n_clusters=n_clusters, init='k-means++', random_state=42)
# kmeans.fit(matrix)
# new_df['Cluster'] = kmeans.labels_
# print(new_df[['video_id','transcript', 'Cluster', 'duplicate']].sort_values(by='Cluster'))

# All done!
print("All done!")

