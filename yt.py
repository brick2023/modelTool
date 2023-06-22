'''
這個 module 可以處理和 youtube 連結相關的東東
pip requirement:
pip install pytube
pip install pydub
'''
from pytube import YouTube 
from pydub import AudioSegment

import os

def yt_url_to_mp3(url, output_path='./', filename='yt-video.mp3'):
    '''
    三個參數 url, output_path='./', filename='yt-video.mp4'
    這個 function 會吃一個 youtube 的 url, 將他輸出成一個 yt-audio.mp3 檔案到指定路徑
    會回傳指定路徑的 path
    '''
    # 輸出 mp3 的路徑
    #output_path = r'./yt-audio.mp3'
    # 建立 YouTube 物件
    yt = YouTube(url)

    # 取得影片的音軌
    audio_stream = yt.streams.filter(only_audio=True).first()
    assert audio_stream is not None # pyright 會跳錯誤提示這樣就不會ㄌ
    # 下載音軌到指定的路徑
    audio_stream.download(output_path="./", filename=filename)

    # 讀取下載下來的音檔
    audio_file = AudioSegment.from_file(output_path+filename)
    os.system(f'rm {output_path+filename}') # 用不到了可以刪除

    # 檢查音檔是否可以正常解碼
    print('audio file(確認解碼):', audio_file)

    # 將音檔轉換為 MP3 格式
    audio_file.export(output_path+filename, format="mp3")
    print(f'成功輸出 {filename}, 路徑為{output_path}')
    
    return output_path+filename

def yt_url_to_mp4(url, output_path='./', filename='yt-video.mp4'):
    yt = YouTube(url)
    mp4_file = yt.streams.filter(file_extension='mp4').first()


    # 下載到路徑
    print(f'影片{filename}正在下載到 {output_path}')
    # assert mp4_360p_files is not None
    mp4_file.download(output_path, filename=filename)
    print('影片下載完成')

# test
# print(yt_url_to_mp3('https://youtu.be/FZYh6lPymJ0'))
# yt_url_to_mp4('https://youtu.be/vxxPtDCb9Go', output_path='./test-video/', filename='ai-class1.mp4')
# yt_url_to_mp4('https://youtu.be/VpKN3KvSK6c', output_path='./test-video/', filename='ai-class2.mp4')
