'''
這個 module 可以處理和 youtube 連結相關的東東
pip requirement:
pip install pytube
pip install pydub
如果遇到 pytube issue 可以參考：https://github.com/pytube/pytube/issues/1678
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
if __name__=='__main__':
    # 台大演算法課程
    # company1_video_name_url={'Lec1 演算法':'https://youtu.be/7a28lIQIHJQ',
    #                         'Lec2 演算法':'https://youtu.be/kxIQ86qMtfk',
    #                         'Lec3 演算法':'https://youtu.be/OVhJHBYJLSE',
    #                         'Lec4 演算法':'https://youtu.be/rP2wm4bEfXo',
    #                         'Lec5 演算法':'https://youtu.be/tTFolqL1TX4',
    #                         'Lec6 演算法':'https://youtu.be/24akv3pVt28',
    #                         'Lec7 演算法':'https://youtu.be/FvUs-OlAy18',
    #                         'Lec8 演算法':'https://youtu.be/r5CTlHdo9Oo',
    #                         'Lec9 演算法':'https://youtu.be/OQDaruIDCjY',
    #                         'Lec10 演算法':'https://youtu.be/hZjp35QI-40',
    #                         'Lec11 演算法':'https://youtu.be/0UGaXukC4b0',
    #                         'Lec12 演算法':'https://youtu.be/yWZHGsd06dA',
    #                         'Lec13 演算法':'',
    #                         'Lec14 演算法':'',
    #                         'Lec15 演算法':'',
    #                         'Lec16 演算法':'',
    #                         'Lec17 演算法':'',
    #                         'Lec18 演算法':'',
    #                         'Lec19 演算法':'',
    #                         'Lec20 演算法':'',
    #                         'Lec21 演算法':'',
    #                         'Lec22 演算法':'',
    #                         'Lec23 演算法':'',
    #                         'Lec24 演算法':'',}
    company1_video_name_url={'Lec13 演算法':'https://youtu.be/trkaH2uLxHw?si=V7_DJump-ti8BEzK',
                            'Lec14 演算法':'https://youtu.be/trkaH2uLxHw?si=KE2aRl-Cqftn1KOV',
                            'Lec15 演算法':'https://youtu.be/62uS-MOv0bY?si=w27sX-PO2PdGx0zk',
                            'Lec16 演算法':'https://youtu.be/sweW4TVFpbQ?si=-pzAfnVtOhjTL28w',
                            'Lec17 演算法':'https://youtu.be/359YMyqbEG4?si=vLrFAH_3UwL1NkMA',
                            'Lec18 演算法':'https://youtu.be/dkmxHij2pfU?si=oQX4pI9JUblUmlwZ',
                            'Lec19 演算法':'https://youtu.be/S5vS9YEvnFU?si=5uZzBSIf5lI0_pee',
                            'Lec20 演算法':'https://youtu.be/lY1SKWSR3pk?si=1KuCEdozXFOB-MII',
                            'Lec21 演算法':'https://youtu.be/NOYNTuhXDGU?si=Yu8uKD9HXdDcTvLJ',
                            'Lec22 演算法':'https://youtu.be/PqN0aJeYtuA?si=HAjuu3aoX8kS7OHP',
                            'Lec23 演算法':'https://youtu.be/6n8vyWKGsIo?si=OeVapPeBOmj5MCbm',
                            'Lec24 演算法':'https://youtu.be/cmQQL_hBBIM?si=JRrTGntXQJmXiwtx',}
    # for name, url in company1_video_name_url.items():
    #     if url != '':
    #         name = name.split(' ')[0]
    #         yt_url_to_mp4(url, output_path='/home/brick/platform/src/video/company1/algorithm/', filename=name+'.mp4')
    #         print(name, url)

# print(yt_url_to_mp3('https://youtu.be/FZYh6lPymJ0'))
# yt_url_to_mp4('https://youtu.be/vxxPtDCb9Go', output_path='./test-video/', filename='ai-class1.mp4')
# yt_url_to_mp4('https://youtu.be/VpKN3KvSK6c', output_path='./test-video/', filename='ai-class2.mp4')

    # 資工研究所考古題解析 (計算機組織，作業系統)
    company2_video_name_url = {'Disk positioning time (97交大資工) - 朱宗賢老師':'https://youtu.be/d59KRMJEIYw?si=gBbs9IJC6_CoCKcY',
                               'Reduce page fault rate (103 交大資工) - 朱宗賢老師':'https://youtu.be/5jrLyPkD4R4?si=cvw93q9vhZBpbPiL',
                               'Effective Memory Access Time (102 成大資工) - 朱宗賢老師': 'https://youtu.be/rLIk12xBJs4?si=Y0aAZTgckIJbkxcf',
                               'RAID Disk Space Calculation (97 交大資工) - 朱宗賢老師':'https://youtu.be/Mr7XAT7VIXI?si=ZQtQ4G_cRoTwAkZO',
                               'The top & bottom half in interrupt handling (99 中央資工) - 朱宗賢老師':'https://youtu.be/N8y28AZqgkw?si=OHi04UNcsIr5NPiQ',
                               'Program structure (1) - increase locality & reduce page faults (99成大資工) - 朱宗賢老師':'https://youtu.be/P6Adyt6jrJg?si=IqmCl5-e3w7ZvB1n',
                               'Program structure (2) - increase locality & reduce page faults (102 清大資工) - 朱宗賢老師':'https://youtu.be/zmM8RR94-Ls?si=UuRF4-KKwXVIoSUg',
                               'File Allocation Methods (99 成大資工) - 朱宗賢老師':'https://youtu.be/n-Wp8O912pk?si=c3YgHq_n0B3VhrIn'
                               }
    for name, url in company2_video_name_url.items():
        name = name.replace(' ', '_')
        print(name)
        output_path = '/home/brick2/platform/src/video/company2/Computer-science-old-exam/'
        # 若是沒有資料夾就建立
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        try:
            yt_url_to_mp4(url, output_path='/home/brick2/platform/src/video/company2/Computer-science-old-exam/', filename=name+'.mp4')
        except Exception as e:
            print(e)
            print('error:', e)
        print(name, url)
