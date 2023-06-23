"""
這個檔案介紹了如何使用 summarize.py 和 mediaKit.py
注意：這個檔案是用來測試的，並不是一個完整的程式
還有，如果使用 xxx list 或是 xxx dict 開頭的函式，雖然可以節省 model load 的時間，但是可能會因為記憶體不足而失敗
尤其是 vicuna 相關的模型，因為模型太大了，所以會吃掉大量記憶體
建議向下方的處理方式，一次只用模型處理一個檔案，這樣就不會有記憶體不足的問題，因為每次都會 unload 模型
"""

import os
from summarize import file_text_dict_to_summary_files, text_to_summary_file
from mediaKit import media_to_text, media_list_to_text_dict

video_path = '/home/brick/yenslife/modelTool/test-video/' # 影片路徑
videos = os.listdir(video_path) # 在 shell 中 ls 的結果放到 list
summary_output_path = '/home/brick/yenslife/modelTool/test-text-data/' # 放摘要檔案的地方

# 取得 file path 的 list
media_path_list = []
for mp4 in os.listdir(video_path):
    media_path_list.append(video_path + mp4)

# 取得 [filepath]:[text] 的字典
file_text_dict = media_list_to_text_dict(media_path_list, 'large')

# 依序處理喂給模型
for path, text in file_text_dict.items():
    filename_with_extension = os.path.basename(path)
    filename = filename_with_extension.split('.')[0] 
    new_path = f"{summary_output_path}{filename}.txt"
    text_to_summary_file(text, new_path)

# 下面這個方法是把 summary 寫入特定路徑檔案們，而只在最一開始 load model 一次，可以省大量時間
# 但是由於目前似乎記憶體不足，會執行到一半失敗
# file_text_dict_to_summary_files(file_text_dict, summary_output_path) # 還可以加上 model path 和 temperature
