"""
Process the data extracted from scrapers and create a data sample
"""

import pickle
import pandas as pd
import re
import os
import numpy as np
from unidecode import unidecode

pd.set_option('display.max_columns', None)

# Get Directory
path_up = os.path.dirname(os.getcwd())

# Load and transform
print("Load and Transform data")

with open(path_up + '/data/video_info_df.pickle', 'rb') as f:
    video_info_df = pickle.load(f)

with open(path_up + '/data/video_stats_df.pickle', 'rb') as f:
    video_stats_df = pickle.load(f)

with open(path_up + '/data/video_transcript_df.pickle', 'rb') as f:
    video_transcript_df = pickle.load(f)

# Consolidate data sources
video_info_df = video_info_df[['video_id', 'title', 'description']]
video_transcript_df = video_transcript_df[['video_id', 'transcript']]
video_stats_df = video_stats_df[['video_id', 'views']]

df_video = video_info_df.merge(video_transcript_df, on='video_id', how='left')
df_video = df_video.merge(video_stats_df, on='video_id', how='left')

print(video_info_df.shape)

df_video = df_video.replace(np.nan, "").drop_duplicates()

# Merging all text for analysis
df_video['all_text'] = df_video['title'] + df_video['description'] + df_video['transcript']

# Read keywords and tag ads based on the brand names they mention
keywords = pd.read_csv(path_up + '/scrapers/keywords.csv')
keywords = keywords.loc[(keywords['Type'] == 'brand') & (keywords['Select'] == 'Y')]

# unidecode standardizes all special punctuations, accent, etc
brands_all = unidecode("|".join(keywords.Name)).lower()

# Define functions to search for keywords within DataFrame text
def brand_keywords(row):
    return re.findall(brands_all, unidecode(row.lower()))

def keywords(row):
    return re.findall('hair|shampoo|conditioner|skincare|volume|damaged|beauty|repair|serum', row.lower())


# Apply to df to identify video categories

df_video['keywords'] = df_video['all_text'].apply(keywords)
df_video['brand_keywords'] = df_video['all_text'].apply(brand_keywords)

df_video['num_keywords'] = df_video['keywords'].apply(lambda x: len(x))
df_video['num_brand_keywords'] = df_video['brand_keywords'].apply(lambda x: len(x))

# Select top videos relevant to our topic

df_top = df_video[['video_id', 'title', 'description', 'transcript', 'all_text',
                   'keywords', 'num_keywords', 'brand_keywords', 'views']].copy()
df_top.sort_values(by='views', ascending=False, inplace=True)

# Select videos with at least 1k views
df_top['views'] = df_top['views'].astype(int)
df_top.fillna(0, inplace=True)

df_top = df_top.loc[(df_top['num_keywords'] >= 1) & (df_top['views'] > 1000)]


def most_common(lst):
    """Selects most common element in a list"""
    if not lst:
        brand = 'No brand'
    else:
        brand = max(set(lst), key=lst.count)
    return brand

# Tag brands within videos, assuming it is the most common brand mentioned
df_top['brand'] = df_top['brand_keywords'].apply(most_common)
df_top['brand'] = df_top['brand'].apply(unidecode).apply(lambda x: x.lower())
top_brands = df_top[['brand', 'views']].groupby('brand').count().sort_values(by='views', ascending=False)

# Select brands with at least 5 videos
top_brands = list(top_brands.loc[top_brands['views'] >= 5].reset_index().brand)

# Filter dataset on selected brands, top 25 videos by brand
df_top = df_top.loc[df_top['brand'].isin(top_brands)]
df_top = df_top.sort_values(by='views', ascending=False).groupby('brand').head(25).reset_index(drop=True)
print(df_top[['brand', 'views']].groupby('brand').count())

with open(path_up + '/files/df_top_videos.pickle', 'wb') as f:
    pickle.dump(df_top, f)
