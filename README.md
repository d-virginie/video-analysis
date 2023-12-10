# Video Analysis
This repo is an exploratory analysis, to scrape and analyse Youtube videos content.
It is designed for Ads analysis.

Note : this hasn't been packaged yet into an app

## Approach

1. Define a list of keywords, download related videos.
2. Create a subset of videos by brand for specific keywords.
3. Process the videos to extract keywords, comments, sentiments
4. Extract the frames from videos
5. Cluster the frames to find main "classic" frame types for this topic/brand

## Usage

Start by running the scrapers:
1. collect_video_ids.py
2. dl_ad_videos.py

Then from the video_signals directory
1. sampling_videos.py
2. processing_videos.py
3. getting_frames.py
4. frames_clustering.py

