"""
Download Youtube videos - Step 1

Collect video ids relevant to our use case using a youtube specific library scrapetube
"""

import scrapetube
import pandas as pd
import pickle
import os

# Read keywords from our file - to be searched for on Youtube

keywords = pd.read_csv('keywords.csv')

beauty_brands = keywords.loc[(keywords["Category"] == 'Beauty & HPC')
                             & (keywords['Type'] == 'brand')
                             & (keywords['Select'] == 'Y')].astype(str)

queries_list = list(beauty_brands.Name)
print(queries_list[1:10])

# Define Search parameters for Youtube Search

limit_videos = 100
limit_channels = 15
search_channels = False
search_videos = True
videos = []


# Putting together the video_id list, to download in subsequent steps
# For each topic, we search videos, then channels, with that keyword

for query in queries_list:
    print(query)

    if search_videos is True:
        print('getting search videos')
        videos_search = scrapetube.get_search(query,
                                              limit=limit_videos, results_type="video")
        for video in videos_search:
            videos.append(video)

    if search_channels is True:
        print('getting channels')
        channel_search = scrapetube.get_search(query,
                                               limit=limit_channels, results_type="channel")
        # Then get videos within the channels
        for channel in channel_search:
            print('getting channel videos')
            videos_channel = scrapetube.get_channel(channel['channelId'], limit=30)
            for video in videos_channel:
                videos.append(video)

os.makedirs('files', exist_ok=True)

# Dump the list in a pickle file
with open('files/videos.pickle', 'wb') as f:
    pickle.dump(videos, f)
