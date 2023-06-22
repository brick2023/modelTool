import os
from ..summarize import text_to_summarize_file
from ..mediaKit import mp4_to_text

video_path = '../test-video/'
videos = os.listdir(video_path)
summarize_output_path = '../test-text-data/'
# print(video_ls)

for video in videos:
    text = mp4_to_text(video_path+video, 'large')
    text_to_summarize_file(text, summarize_output_path)

