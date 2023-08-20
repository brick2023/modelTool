''' 
這個檔案用來生成課程的影片和gif
這是對應主機"~/platform/src"資料夾裡面的格式去做的
執行這個程式會去到"~/platform/src/img"裡面對應"~/platform/src/video"創建課程資料夾
所有的課程資料夾中再創建一個screenshot和gif資料夾
分別用來存當封面的課程影片的截圖和預覽用的gif

環境必須的套件：
pip install moviepy
pip install ffmpeg
'''
from moviepy.editor import *
import os

def video_screenshot(video_path: str , screenshot_file_path: str):
    '''
    截取影片時長的一半當作該課程影片的封面
    video_path 應該會長這樣: "~/platform/src/video/company1/algorithm/Lec01.mp4"
    screenshot_file_path 應該會長這樣: "~/platform/src/img/company1/algorithm/screenshot"
    '''
    course_path = os.path.dirname(video_path) # Ex: "~/platform/src/video/company1/algorithm/"
    
    lesson = video_path.replace(course_path , "") # Ex: "Lec01.mp4"
    lesson = lesson.replace(".mp4" , "") # Ex: "Lec01"
    
    video = VideoFileClip(video_path)
    
    screenshot = video.save_frame(screenshot_file_path + lesson + ".jpg", t = (video.duration / 2))
    print('ok')
    video.close()
    
def video_to_gif(video_path: str , gif_file_path:str):
    '''
    將影片分成6小段然後合併成一個影片
    再將合併後的這段影片轉成gif
    video_path 應該會長這樣: "~/platform/src/video/company1/algorithm/Lec01.mp4"
    gif_file_path 應該會長這樣: "~/platform/src/img/company1/algorithm/gif"
    '''
    course_path = os.path.dirname(video_path) # Ex: "~/platform/src/video/company1/algorithm/"
        
    lesson = video_path.replace(course_path , "") # Ex: "Lec01.mp4"
    lesson = lesson.replace(".mp4" , "") # Ex: "Lec01"
     
    video = VideoFileClip(video_path)
    secStart = video.duration / 6
    segments = []
    for i in range(1 , 6):
        segment = video.subclip((secStart * i) - 1 , (secStart * i) + 1)
        segments.append(segment)

    video_concat = concatenate_videoclips(segments)
    video_concat.write_gif(gif_file_path + lesson + ".gif" , fps = 10)
    print('ok')
    video.close()
    
def create_img_dir(video_dir_path: str):
    '''
    在src/img的資料夾中創建和video一模一樣的資料夾結構
    如果已經擁有的資料夾就不會再創建
    video_dir_path大概長這樣: "~/platform/src/video/"
    '''   
    img_dir_path = video_dir_path.replace("video" , "img") # Ex: "~/platform/src/img/"
    
    all_company_list = os.listdir(video_dir_path)
    
    for i in all_company_list:
        company_name = os.path.join(video_dir_path , i) # Ex: "~/platform/src/video/company1"
        company_name_img = os.path.join(img_dir_path , i) # Ex: "~/platform/src/img/company1"
        if not os.path.isdir(company_name_img):
            os.mkdir(company_name_img)
            
        course_list = os.listdir(company_name)
        for j in course_list:
            course_name = os.path.join(company_name , j) # Ex: "~/platform/src/video/company1/algorithm"
            course_name_img = os.path.join(company_name_img , j) # Ex: "~/platform/src/img/company1/algorithm"
            if not os.path.isdir(course_name_img):
                os.mkdir(course_name_img)
            #每個課程中都要有一個screenshot和gif的資料夾
            screenshot = os.path.join(course_name_img , "screenshot") # Ex: "~/platform/src/img/company1/algorithm/screenshot"
            gif = os.path.join(course_name_img , "gif") # Ex: "~/platform/src/img/company1/algorithm/gif"
            if not os.path.isdir(screenshot):
                os.mkdir(screenshot)
            if not os.path.isdir(gif):
                os.mkdir(gif)

if __name__=='__main__':
    video_path = os.path.expanduser("~/platform/src/video") #進入存放課程的資料夾
    '''
    os.path可以根據你輸入的路徑的形式去判斷他join的時候要怎麼加
    所以video_path只要根據執行這個程式時使用的環境去輸入相對應的路徑就可以了。
    比方說主機的話路徑就是"~/platform/src/video/"
    Windows就是"C:\\Users\\booke\\platform\\src\\video"
    '''
    create_img_dir(video_path)
    
    all_company_list = os.listdir(video_path)
    
    for i in all_company_list:
        company_name = os.path.join(video_path , i) # Ex: "~/platform/src/video/company1"
        course_list = os.listdir(company_name)
        for j in course_list:
            course_name = os.path.join(company_name , j) # Ex: "~/platform/src/video/company1/algorithm"
            course_units = os.listdir(course_name)
            for k in course_units:
                lesson = os.path.join(course_name , k) # Ex: "~/platform/src/video/company1/algorithm/Lec1.mp4"
                img_file_path = os.path.dirname(lesson) # Ex: "~/platform/src/video/company1/algorithm/"
                img_file_path = img_file_path.replace("video" , "img") # Ex: "~/platform/src/img/company1/algorithm/"
                
                screenshot_file_path = os.path.join(img_file_path , "screenshot") # Ex: "~/platform/src/img/company1/algorithm/screenshot"
                gif_file_path = os.path.join(img_file_path , "gif") # Ex: "~/platform/src/img/company1/algorithm/gif"
                video_screenshot(lesson , screenshot_file_path)
                video_to_gif(lesson , gif_file_path)    
                  