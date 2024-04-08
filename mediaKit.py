''' 
這個檔案主要處理和影片、音訊有關的工具包，使用 openai whisper 來轉換音訊
所有中間處理的檔案都會被自動刪除，只留下目標檔案所以請安心使用 by yenslife

環境必須的套件：
pip install openai-whisper 
pip install moviepy

conda install -c conda-forge ffmpeg
'''

import whisper
from whisper.utils import get_writer
# from .yt import yt_url_to_mp3 # 測試用
from moviepy.editor import VideoFileClip
import os 
import time # 測試用
import gc
from opencc import OpenCC

def media_to_text(media_path, model_size='base'):
    '''
    media_path(mp3或是mp4的路徑, model_size)
    其中 model_size 預設是 base，可以是 tiny, base, small, medium, large 看你要犧牲精確度還是時間
    讀取 MP3 or MP4 檔案，轉成文字檔案
    '''
    print(f'whisper model(模型大小為：{model_size}) 正在載入...')
    model = whisper.load_model(model_size)
    print(f'whisper 正在轉換文字...')
    result = model.transcribe(media_path, fp16=False, language='zh')
    print('成功從 mp3 取得文字')
    del model # 清除記憶體
    gc.collect() # 清除記憶體
    return result['text']

def media_to_srt_file(media_path, output_file_path=r'./out.srt', model_size='base'):
    """
    將 mp3 or mp4 轉成 srt 檔案
    給第一個參數 mp3 or mp4 路徑
    第二個參數是輸出 srt 路徑(預設為 ./out.srt)
    第三個參數是要使用的轉換模型大小(預設為 base)
    """
    language = 'zh'
    print(f'whisper model(模型大小為：{model_size}) 正在載入...')
    model = whisper.load_model(model_size)
    print(f'whisper 正在轉換文字...')
    result = model.transcribe(media_path, fp16=False, language=language)
    srt_writer = get_writer("srt", os.path.dirname(output_file_path))
    directory = os.path.dirname(output_file_path)
    # 檢查資料夾是否存在
    if not os.path.exists(directory):
        os.makedirs(directory)
    srt_writer(result, media_path)
    print(f'成功將文字輸出到檔案路徑:{output_file_path}')
    return output_file_path

def media_list_to_srt_files(media_path_list, output_dir=r'./test-text-data/', model_size='base'):
    """
    將 mp3 or mp4 的路徑 list 轉成 srt 檔案到指定的資料夾
    第一個參數是 mp3 or mp4 的路徑 list
    第二個參數是輸出 srt 路徑(預設為 ./test-text-data/)
    第三個參數是要使用的轉換模型大小(預設為 base)
    """
    language = 'zh'
    print(f'whisper model(模型大小為：{model_size}) 正在載入...')
    model = whisper.load_model(model_size)
    print(f'whisper 正在轉換文字...')
    for path in media_path_list:
        print(f'正在處理 {path}...')
        result = model.transcribe(path, fp16=False, language=language)
        srt_writer = get_writer("srt", output_dir)
        srt_writer(result, path)
        print(f'成功將文字輸出到檔案路徑:{output_dir}')
    return output_dir

def text_to_file(text, output_file_path=r'./out.txt'):
    '''
    text_to_file(文字, 檔案路徑)
    將文字輸出到指定的檔案路徑(預設為 ./out.txt)
    '''
    f = open(output_file_path, 'w')
    f.write(text)
    f.close()
    print(f'成功將文字輸出到檔案路徑:{output_file_path}')
    return output_file_path

def media_to_text_file(media_path, text_file_path=r'./out.txt', model_size='base'):
    '''
    media_to_text_file(media_path, text_file_path=r'./out.txt', model_size='base') 共有三個參數

    media_path: 要轉換的 mp3 or mp4 路徑
    text_file_path: 要輸出的 txt 路徑(預設為 out.txt)
    model_size: 要使用的轉換模型大小(預設為 base)
    '''
    text = media_to_text(media_path, model_size) # mp3 or mp4 轉文字
    return text_to_file(text, text_file_path) # 文字轉檔案

def mp4_to_mp3(mp4_path, mp3_path='./mp4-to-mp3.mp3'):
    '''
    將 mp4 轉成 mp3 檔案
    第一個參數 mp4 路徑
    第二個參數輸出 mp3 路徑(預設為 ./mp4-to-mp3.mp3)
    '''
    video = VideoFileClip(mp4_path)
    assert video.audio is not None
    video.audio.write_audiofile(mp3_path) # 這邊 nvim 會報錯不知道為什麼，但是實際上是沒錯的，所以要加上 assert 跟他講一下
    return mp3_path

def media_list_to_text_dict(media_path_list, model_size='base'):
    '''
    給定 mp3 or mp4 路徑 list，將裡面的檔案都轉成 text，回傳一個 dict() -> [影片名稱]:[text]
    可以指定 model_size
    這麼做的好處是可以節省不必要的 load model 時間
    Args:
        media_path_list: mp3 or mp4 的路徑 list. e.g. ['./test-video/ai-class1.mp4', './test-video/ai-class2.mp4']
        model_size: whisper model 的大小，常見的是 'base', 'medium', 'large'，詳情請參考 openai whisper
    Returns:
        回傳一個 dict() -> [影片名稱]:[text]
    '''

    # loading model
    print(f'whisper model(模型大小為：{model_size}) 正在載入...')
    model = whisper.load_model(model_size)
    out_dict = dict()

    for meida_path in media_path_list:
        print(f'whisper {model_size} 正在將 {meida_path} 轉換成文字...')
        result = model.transcribe(meida_path, fp16=False, language='zh')
        text = result['text']
        out_dict[meida_path] = text

    # clean
    del model # 釋放記憶體
    gc.collect() # 釋放記憶體

    return out_dict

def media_list_to_text_files(media_path_list, output_file_path, model_size='base'):
    """
    給定 mp3 or mp4 路徑 list，將裡面的檔案都轉成 text
    會做出一個 dict() -> [影片名稱]:[text]，並將他輸出到 output_file_path
    檔名為 mp3 or mp4 的檔名
    可以指定 model_size
    這麼做的好處是可以節省不必要的 load model 時間
    Args:
        media_path_list: mp3 or mp4 的路徑 list
        output_file_path: 輸出的多個 txt 檔案的指定路徑
        model_size: whisper model 的大小，常見的是 'base', 'medium', 'large'，詳情請參考 openai whisper
    Returns:
        回傳 output_file_path
    """
    out_dict = media_list_to_text_dict(media_path_list, model_size)
    for key, value in out_dict.items():
        filename = os.path.basename(key)
        filename = filename.split('.')[0]
        f = open(f'{output_file_path}/{filename}.txt', 'w')
        f.write(value)
    print(f'已寫入所有檔案到{output_file_path}')
    return output_file_path
def media_list_to_text_and_srt_files(media_path_list, text_output_dir_path, srt_output_dir_path, model_size='base'):
    """
    給定 mp3 or mp4 路徑 list，將裡面的檔案都轉成 text 和 srt
    會做出一個 dict() -> [影片名稱]:[text]，並將他輸出到 text_output_dir_path, srt_output_dir_path
    檔名為 mp3 or mp4 的檔名
    """
    language = 'zh'
    print(f'whisper model(模型大小為：{model_size}) 正在載入...')
    model = whisper.load_model(model_size)
    print(f'whisper 正在轉換文字...')
    cc = OpenCC('s2twp')
    for path in media_path_list:
        print(f'正在處理 {path}...')
        result = model.transcribe(path, fp16=False, language=language)
        # 先處理 text
        text = result['text']
        text = cc.convert(text)
        with open(path, 'w') as f:
            f.write(text)
        print(f'成功將文字輸出到檔案路徑:{text_output_dir_path}(已完成繁體中文轉換)')
        # 再處理 srt
        # 注意要先建立資料夾
        directory = os.path.dirname(srt_output_dir_path)
        # 檢查資料夾是否存在
        if not os.path.exists(directory):
            os.makedirs(directory)
        srt_writer = get_writer("srt", srt_output_dir_path)
        srt_writer(result, path)
        filename = os.path.basename(path)
        filename = filename.split('.')[0]
        str_output_file_path = f'{srt_output_dir_path}/{filename}.srt'
        print(f'成功srt輸出到檔案路徑:{str_output_file_path}')
        # 轉換繁體中文
        with open(str_output_file_path, 'r') as f:
            text = f.read()
        text = cc.convert(text)
        with open(str_output_file_path, 'w') as f:
            f.write(text)
        print(f'成功將 {str_output_file_path} 轉換成繁體中文')
    return text_output_dir_path, srt_output_dir_path

def dir_to_text_and_srt_files(input_dir_path, text_output_dir_path, srt_output_dir_path, model_size='base'):
    """
    給定一個資料夾，將裡面的 mp3 or mp4 檔案都轉成 text 和 srt
    會做出一個 dict() -> [影片名稱]:[text]，並將他輸出到 text_output_dir_path, srt_output_dir_path
    檔名為 mp3 or mp4 的檔名
    """
    file_list = os.listdir(input_dir_path)
    print(f'file_list: {file_list}')
    media_path_list = [os.path.join(input_dir_path, file) for file in file_list]
    print(f'media_path_list: {media_path_list}')
    # 如果 text_output_dir_path 不存在就建立
    if not os.path.exists(text_output_dir_path):
        os.makedirs(text_output_dir_path)
    if not os.path.exists(srt_output_dir_path):
        os.makedirs(srt_output_dir_path)
    return media_list_to_text_and_srt_files(media_path_list, text_output_dir_path, srt_output_dir_path, model_size)
    
if __name__=='__main__':
    # media_to_srt_file('/home/brick/platform/src/video/company1/algorithm/Lec1.mp4', './test-text-data/Lec1.srt', model_size='base')
    # media_list_to_srt_files(['/home/brick2/platform/src/video/company1/algorithm/Lec14.mp4', '/home/brick2/platform/src/video/company1/algorithm/Lec15.mp4',
    #                          '/home/brick2/platform/src/video/company1/algorithm/Lec16.mp4', '/home/brick2/platform/src/video/company1/algorithm/Lec17.mp4',
    #                          '/home/brick2/platform/src/video/company1/algorithm/Lec18.mp4', '/home/brick2/platform/src/video/company1/algorithm/Lec19.mp4',
    #                          '/home/brick2/platform/src/video/company1/algorithm/Lec20.mp4', '/home/brick2/platform/src/video/company1/algorithm/Lec21.mp4'
    #                          '/home/brick2/platform/src/video/company1/algorithm/Lec22.mp4', '/home/brick2/platform/src/video/company1/algorithm/Lec23.mp4',
    #                          '/home/brick2/platform/src/video/company1/algorithm/Lec24.mp4'], './test-text-data/', model_size='large')
    # media_list_to_text_files(['/home/brick2/platform/src/video/company1/algorithm/Lec14.mp4', '/home/brick2/platform/src/video/company1/algorithm/Lec15.mp4',
    #                          '/home/brick2/platform/src/video/company1/algorithm/Lec16.mp4', '/home/brick2/platform/src/video/company1/algorithm/Lec17.mp4',
    #                          '/home/brick2/platform/src/video/company1/algorithm/Lec18.mp4', '/home/brick2/platform/src/video/company1/algorithm/Lec19.mp4',
    #                          '/home/brick2/platform/src/video/company1/algorithm/Lec20.mp4', '/home/brick2/platform/src/video/company1/algorithm/Lec21.mp4'
    #                          '/home/brick2/platform/src/video/company1/algorithm/Lec22.mp4', '/home/brick2/platform/src/video/company1/algorithm/Lec23.mp4',
    #                          '/home/brick2/platform/src/video/company1/algorithm/Lec24.mp4'], './test-text-data2/', model_size='large')
    # media_list_to_text_and_srt_files([ '/home/brick2/platform/src/video/company1/algorithm/Lec21.mp4',
    #                                   '/home/brick2/platform/src/video/company1/algorithm/Lec22.mp4', '/home/brick2/platform/src/video/company1/algorithm/Lec23.mp4',
    #                                   '/home/brick2/platform/src/video/company1/algorithm/Lec24.mp4'], '/home/brick2/platform/src/video-info/company1/algorithm/', '/home/brick2/platform/src/srt/company1/algorithm/', model_size='large')
    # media_list_to_text_and_srt_files(['/home/brick2/platform/src/video/company1/algorithm/Lec13.mp4'], '/home/brick2/platform/src/video-info/company1/algorithm/', '/home/brick2/platform/src/srt/company1/algorithm/', model_size='large')
    media_list_to_text_and_srt_files(['/home/brick2/video_mp4/1_國中七下生物/暖身/108新課綱｜國中七下生物｜【暖身】人類與環境的關係.mp4'], '/home/brick2/DataPrepTool/plain_text', '/home/brick2/DataPrepTool/srt', model_size='tiny')
