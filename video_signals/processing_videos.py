"""
Extracting signals from videos
"""

import pickle
import pandas as pd
import os
from transformers import pipeline
from translate import Translator
from keybert import KeyBERT
from collections import Counter
from transformers import pipeline

from scrapers.yt_dl_functions import get_yt_comments

# Get Directory
path_up = os.path.dirname(os.getcwd())

# Load and transform
print("Load and Transform data")

with open(path_up + '/files/df_top_videos.pickle', 'rb') as f:
    df_top = pickle.load(f)

# Get Video Comments

print("Extracting comments from Youtube")
list_videos = list(df_top.video_id)
dict_comments = {}

i = 0
for video in list_videos:
    i += 1
    print(str(round(i / len(list_videos), 2) * 100) + "%")
    dict_comments[video] = [get_yt_comments(video[3:])]  # Cut the prefix 'yt_' from video_id

df_comments = pd.DataFrame.from_dict(dict_comments, orient='index', columns=['comments'])
df_comments = df_comments.reset_index()
df_comments.columns = ['video_id', 'comments']

# Merge new data with our df_top dataframe
df_top_comments = df_top.merge(df_comments, on='video_id', how='left')

# Get Number of comments and ratio comments/views as a gauge of organic activity
df_top_comments['num_comments'] = df_top_comments['comments'].apply(lambda x: len(x))
df_top_comments['comments_ratio'] = df_top_comments['num_comments'] / df_top_comments['views'] * 100

df_top_comments.sort_values(by='comments_ratio', ascending=False, inplace=True)
df_top_comments.reset_index(drop=True, inplace=True)

# Count the number of distinct brands mentioned per video, is it one or several brands?
df_top_comments['num_brands'] = df_top_comments['brand_keywords'].apply(lambda x: len(list(set(x))))

# Translation & Sentiment
print("Translating & getting comments sentiment")

translator = Translator(to_lang="en")

# Translating title and description to English. Transcript is already in English
df_top_comments['en_title'] = df_top_comments['title'].apply(lambda x: translator.translate(x))
df_top_comments['en_description'] = df_top_comments['description'].apply(lambda x: translator.translate(x))

# Create Df column
df_top_comments['sentiment_detail'] = ""

# Use the HuggingFace transformers to get sentiment
sentiment_pipeline = pipeline("sentiment-analysis")

# Using iterrows which isn't very fast, to skip rows with no comments
for index, row in df_top_comments.iterrows():
    data = row['comments']
    if not data:
        df_top_comments.at[index, 'sentiment_detail'] = {}
    else:
        comments_sentiments = sentiment_pipeline(data)
        df_top_comments.at[index, 'sentiment_detail'] = comments_sentiments
        print(comments_sentiments)


# Look at main topics within video transcripts
texts = list(df_top_comments['transcript'])

# Get topics
print("Get Topics per video")

kw_model = KeyBERT()
keywords = [kw_model.extract_keywords(text, top_n=7) for text in texts]

list_kw = [kw[0] for k_list in keywords for kw in k_list]

print(Counter(list_kw))

# Get zero-shot classification for each video transcript, by top user concern
print("Get zero-shot classification per video")

top_concerns = ['treatment', 'damaged', 'strong hair', 'dandruff', 'smooth', 'coloured', 'feminist',
                'self-confidence', 'busy woman', 'discrimination', 'social image', 'science', 'natural']


classifier = pipeline("zero-shot-classification",
                      model="facebook/bart-large-mnli")

dict_topics = {}

df_top_comments['classification'] = ""

# Using iterrows to skip over empty transcripts
for index, row in df_top_comments.iterrows():
    text = row['transcript']
    if not text:
        df_top_comments.at[index, 'classification'] = ([],[])
    else:
        res = classifier(' '.join(text.splitlines()), top_concerns, multi_label=True)
        df_top_comments.at[index, 'classification'] = (res['labels'], res['scores'])

with open(path_up + '/files/transcript_classified.pickle', 'wb') as f:
    pickle.dump(df_top_comments, f)


print("All done!")
