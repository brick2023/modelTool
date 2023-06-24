"""
這個檔案介紹了如何使用 summarize.py 和 mediaKit.py 的 function
注意：這個檔案是用來測試的，並不是一個完整的程式，不能直接執行，要把他放到 modelTool 外面才能執行（因為路徑問題）
所以請依照自身情況修改路徑，並且把這個檔案放到 modelTool 外面，然後執行
e.g. 路徑修改完成後 -> cp example.py ../ && cd .. && python example.py

還有，如果使用 xxx list 或是 xxx dict 開頭的函式，雖然可以節省 model load 的時間，但是可能會因為記憶體不足而失敗
尤其是 vicuna 相關的模型，因為模型太大了，所以會吃掉大量記憶體 (whisper 目前沒有這個問題)
建議參照下方的處理方式，一次只用模型處理一個檔案，這樣就不會有記憶體不足的問題，因為每次都會 reload 模型(但是會比較慢)
"""

import os # 這個是用來取得檔案路徑的函式
from summarize import file_text_dict_to_summary_files, text_to_summary_file # 這個是用來產生摘要檔案的函式
from mediaKit import media_to_text, media_list_to_text_dict                 # 這個是用來把影片轉成文字的函式

video_path = '/home/brick/yenslife/modelTool/test-video/'              # 影片路徑
videos = os.listdir(video_path)                                        # 在 video_path 底下的所有檔案
summary_output_path = '/home/brick/yenslife/modelTool/test-text-data/' # 摘要檔案的輸出路徑
model_path = '/home/brick/yenslife/model/vicuna-7b/'                   # 模型路徑(其實呼叫 summarize.py 也已經有預設值，可以不用給)

# 取得 file path 的 list
media_path_list = []
for mp4 in os.listdir(video_path):
    media_path_list.append(video_path + mp4) # 把路徑加進去

# 取得 [filepath]:[text] 的字典(dict)
file_text_dict = media_list_to_text_dict(media_path_list, 'large')

# 依序喂文字資料 (prompt) 給模型
for path, text in file_text_dict.items():
    filename_with_extension = os.path.basename(path)            # 取得有副檔名的檔名
    filename = filename_with_extension.split('.')[0]            # 取得沒有副檔名的檔名
    new_path = f"{summary_output_path}{filename}.txt"           # 摘要檔案的路徑
    text_to_summary_file(text, new_path, model_path=model_path, temperature=0.5) # 產生摘要檔案

# 下面這個方法是把 summary 寫入特定路徑檔案們，而只在最一開始 load model 一次，可以省大量時間
# 但是由於目前似乎記憶體不足，會執行到一半失敗
# file_text_dict_to_summary_files(file_text_dict, summary_output_path, model_path=model_path) # 還可以加上 model path 和 temperature
