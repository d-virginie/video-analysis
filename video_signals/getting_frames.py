"""
Extract Video Frames from videos
"""

import cv2
import os
import pickle

path_up = os.path.dirname(os.getcwd())

video_path = '/videos'
image_save_path = '/video_frames'

with open(path_up + '/files/df_top_videos.pickle', 'rb') as f:
    df = pickle.load(f)

list_videos = list(df.video_id)


# Create a function to extract frames from videos with openCV
def extract_images(path_in, path_out):
    count = 0
    vidcap = cv2.VideoCapture(path_in)
    success, image = vidcap.read()

    # Save frames while the video is getting processed, 1 frame per second
    while success:
        vidcap.set(cv2.CAP_PROP_POS_MSEC, (count * 1000))
        success, image = vidcap.read()

        scale_percent = 640/image.shape[1]  # percent of original size
        width = int(image.shape[1] * scale_percent)
        height = int(image.shape[0] * scale_percent)
        dim = (width, height)
        image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
        print('Read a new frame: ', success)
        cv2.imwrite(path_out + "_frame_%d.jpg" % count, image)     # save frame as JPEG file
        count += 1


for video_name in list_videos:
    print(video_name)
    try:
        path_in = path_up + video_path + '/' + video_name + '.mp4'
        path_out = path_up + image_save_path + '/' + video_name
        extract_images(path_in, path_out)

    except Exception as e:
        print(video_name + " Error:")
        print(e)
        pass
