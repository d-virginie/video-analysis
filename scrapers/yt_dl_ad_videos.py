"""
Download Youtube videos - Step 2

Download videos from video_ids previously selected
"""

from yt_dl_functions import video_pytube_dl, get_video_transcript, \
    get_videos_stats, get_yt_video_info
import time
import os
import pandas as pd
import pickle

# Get Directory
path_up = os.path.dirname(os.getcwd())

# Load the video ids from step 1

with open('files/videos.pickle', 'rb') as f:
    videos = pickle.load(f)

# Check if we already have a file where we stored videos that returned an error (not available..)
try:
    with open('files/error_videos.pickle', 'rb') as f:
        videos_error = pickle.load(f)
except:
    videos_error = []

# Get list of videos that are under 1 minute

list_videos = []

for video in videos[0:100]:
    print('cleaning video list')
    try:
        vid_length = video["lengthText"]["simpleText"]

        # Check if video is already downloaded
        if os.path.isfile(path_up + '/videos/yt_' + video['videoId'] + '.mp4'):
            pass
        elif video['videoId'] in videos_error:
            pass
        else:  # Parse the length of video duration to check if video is under 1 minute
            if vid_length.split(":")[:-1][-1] in ('0', '00'):
                list_videos.append(video['videoId'])
    except:
        pass

# Download videos and extract data such as KPIs etc

list_downloaded = []
list_error = []

video_info_df = pd.DataFrame()
video_stats_df = pd.DataFrame()
video_transcript_df = pd.DataFrame()

i = 0
for vid in list_videos:
    i += 1

    # Print progress
    print(str(i) + ". " + vid + " " + str(round(i / len(list_videos), 2) * 100) + "%")

    print('Downloading Video')
    vid_dl, height, width = video_pytube_dl(vid, path_up)

    if vid_dl is not None:  # Continue only if no error

        list_downloaded.append(vid_dl)

        print('Get Transcript')
        transcript_en = get_video_transcript(vid, 'en', path_up)

        print('Get Video Stats')
        _, likes = get_videos_stats(vid)

        print('Get Video Info')
        video_info = get_yt_video_info(vid)

        # Store timestamp
        timestamp_now = round(time.time() * 1000)

        # Store datapoints in a dict
        video_info_dict = dict(video_id="yt_" + vid,
                               timestamp=timestamp_now,
                               platform='youtube',
                               platform_video_id=vid,
                               url='https://youtu.be/' + vid,
                               length_seconds=video_info['duration'],
                               type='ad',
                               video_height=height,
                               video_width=width,
                               topics=video_info['keywords'],
                               title=video_info['title'],
                               description=video_info['description'],
                               channel=video_info['channel_name'],
                               channel_id=video_info['channel_id'],
                               publish_date=video_info['publish_date'],
                               brand='unknown',
                               country=video_info['country'])

        video_stats_dict = dict(video_id="yt_" +vid,
                                timestamp=timestamp_now,
                                likes=likes,
                                share=0,
                                save=0,
                                views=video_info['views'],
                                kpi="",
                                kpi_value="",
                                reach=0,
                                target_country="",
                                budget="")

        video_transcript_dict = dict(video_id="yt_" +vid,
                                     language='en',
                                     transcript=transcript_en)

        info_df = pd.DataFrame([video_info_dict])
        stats_df = pd.DataFrame([video_stats_dict])
        trans_df = pd.DataFrame([video_transcript_dict])

        video_info_df = pd.concat([video_info_df, info_df], axis=0, ignore_index=True)
        video_stats_df = pd.concat([video_stats_df, stats_df], axis=0, ignore_index=True)
        video_transcript_df = pd.concat([video_transcript_df, trans_df], axis=0, ignore_index=True)

        with open('files/list_downloaded.pickle', 'wb') as f:
            pickle.dump(list_downloaded, f)
    else:
        list_error.append(vid)
        with open('files/error_videos.pickle', 'wb') as f:
            pickle.dump(list_error, f)

print(video_info_df.shape)

# Dump the data pickle files
with open(path_up + '/data/video_info_df.pickle', 'wb') as f:
    pickle.dump(video_info_df, f)

with open(path_up + '/data/video_stats_df.pickle', 'wb') as f:
    pickle.dump(video_stats_df, f)

with open(path_up + '/data/video_transcript_df.pickle', 'wb') as f:
    pickle.dump(video_transcript_df, f)