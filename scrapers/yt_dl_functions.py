"""Functions used for downloading videos and storing data"""

from pytube import YouTube
import os
import pandas as pd
import cv2
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_comment_downloader import YoutubeCommentDownloader
from youtubesearchpython import Video, ResultMode
from bs4 import BeautifulSoup


def video_pytube_dl(video_id, download_url):
    """ Function that downloads youtube videos into a folder.

    Args:
        video_id : youtube video id
        download_url : the full path to the folder where you want to
         download the video.
         Example '/Users/xyz/Downloads/short_form_videos'

    Returns:
        video_id downloaded
        """

    try:
        yt = YouTube('https://youtube.com/watch?v='+video_id)
        dl = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        out_file = dl.download(download_url+'/videos')
        os.rename(out_file, download_url+'/videos/yt_'+video_id+'.mp4')
        # get video aspect ratio
        vid = cv2.VideoCapture(download_url+'/videos/yt_'+video_id+'.mp4')
        height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)

        return_video = video_id, height, width

    except Exception as e:
        return_video = None, 0, 0
        print("Cannot download video: ")
        print(e)

        # with open(download_url+'/files/error_videos.pickle', 'ab') as f:
        #     pickle.dump(video_id, f)

    return return_video


def get_video_transcript(video_id, language_trans, download_url, mode='txt_return'):
    """ Function that returns transcript text or downloads youtube
    videos transcript into a csv file.

    Args:
        video_id : youtube video id
        language_trans : the transcript language to download. Example 'en'.
        download_url : the full path to the folder where you want to
         download the video.
         Example '/Users/xyz/Downloads/short_form_videos'
        mode : 'txt_save' downloads in text file,
        'txt_return' returns the text (default)
    Returns:
        video_id downloaded
        """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_trans])
        text = str()

        for trans in transcript:
            sentence = trans.get("text")
            text = text + "\n" + sentence

        if mode == 'txt_save':
            # write in text file
            text_file = open(download_url + "/transcripts/yt_" + video_id + ".txt", "w")
            text_file.write(text)
            text_file.close()
            return_transcript = video_id
        elif mode == 'txt_return':
            return_transcript = text
        else:
            return_transcript = None
    except:
        return_transcript = None

    return return_transcript


def get_yt_comments(video_id):
    """ Function that retrieves youtube videos comments as a list.

    Args:
        video_id : youtube video id
    Returns:
        list of comments
        """
    try:
        downloader = YoutubeCommentDownloader()  # initialize the instance outside?
        comments = downloader.get_comments_from_url('https://www.youtube.com/watch?v=' + str(video_id))
        list_comments = [dict_com["text"] for dict_com in comments]
    except:
        list_comments = []

    return list_comments


def get_yt_video_info(video_id):
    """ Function that retrieves youtube videos stats and details.

    Args:
        video_id : youtube video id
    Returns:
        A dictionary with title, description, keywords, views, etc.
        """
    video_info = Video.getInfo('https://youtu.be/' + str(video_id), mode=ResultMode.json)

    # Get country details from Channel - too slow
    # channel_country = Channel.get(video_info["channel"]["id"])["country"]

    dict_vid = dict(video_id=video_info["id"],
                    title=video_info["title"],
                    duration=video_info["duration"]["secondsText"],
                    views=video_info["viewCount"]["text"],
                    thumbnail=video_info["thumbnails"][0]["url"],
                    description=video_info["description"],
                    channel_name=video_info["channel"]["name"],
                    channel_id=video_info["channel"]["id"],
                    country="",
                    keywords=video_info["keywords"],
                    publish_date=video_info["publishDate"])
    return dict_vid


def get_videos_stats(video_id):
    """ Function that retrieves youtube videos views and likes.

    Args:
        video_id : youtube video id
    Returns:
        views, likes
        """
    try:
        video_url = "https://www.youtube.com/watch?v="+video_id
        response = requests.get(video_url)

        soup = BeautifulSoup(response.content, 'html.parser')
        views = soup.find("div", class_="watch-view-count").text
        likes = soup.find("button", class_="like-button-renderer-like-button").text
    except:
        views = 0
        likes = 0

    return views, likes


def save_csv(dict_data, name_dict, dl_url):
    dict_data_df = pd.DataFrame([dict_data])

    os.makedirs(dl_url + '/data', exist_ok=True)

    if os.path.isfile(dl_url + '/data/' + name_dict + '.csv'):  # If file exists we skip header
        dict_data_df.to_csv(dl_url + '/data/' + name_dict + '.csv', index=False, header=False, mode='a')
    else:
        dict_data_df.to_csv(dl_url + '/data/' + name_dict + '.csv', index=False, header=True)

    return None
