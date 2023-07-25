# -*- coding: utf-8 -*-
"""
與搜尋相關的函式
"""

from fuzzywuzzy import fuzz, process

def fuzzy_search(query, data):
    """
    這個函式會回傳一個 list，裡面包含了所有符合的結果的 tuple 格式為: (文本, 相似度)
    每個結果都是一個 tuple，包含了 (名稱, 相似度)
    接收兩個參數 query 和 data 分別代表使用者輸入的字串和要比對的資料
    """
    results = []
    for item in data:
        if item is None:
            item = ''
        score = fuzz.partial_ratio(query.lower(), item.lower())
        results.append((item, score))
    results.sort(key=lambda x: x[1], reverse=True) # 依照分數由高到低排序
    return results

def parse_srt_file(filename):
    subtitles = []
    if filename is None:
        return subtitles
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.isdigit():  # Check if it's a subtitle number
            start_time, end_time = lines[i + 1].strip().split(' --> ')
            subtitle = ' '.join(lines[i + 2:i + 2 + lines[i + 2:].index('\n')])
            subtitles.append((start_time, end_time, subtitle))
            i = i + 3 + lines[i + 3:].index('\n')  # Move to the next subtitle
        i += 1

    return subtitles

def search_parsed_srt(keyword, data_list):
    result = []
    
    for data in data_list:
        time_start, time_end, subtitle = data
        similarity = fuzz.ratio(subtitle, keyword)
        result.append((similarity, data))
    
    # 將結果根據相關性進行排序，相關性高的排在前面
    result.sort(key=lambda x: x[0], reverse=True)
    
    # 只保留資料本身，去掉相關性分數，只輸出前十
    sorted_data_list = [data[1] for data in result if data[0] >= 30]
    sorted_data_list = sorted_data_list[:10]
    return sorted_data_list

# 這個函式會是最棒的，之後要加入翻譯功能也加在這裏面
def srt_search(keyword, filepath):
    subtitles = parse_srt_file(filepath)
    result = search_parsed_srt(keyword, subtitles)
    from datetime import datetime
    def time_key(time_str):
        return datetime.strptime(time_str, '%H:%M:%S,%f')
    result.sort(key=lambda x: time_key(x[0]))
    return result

if __name__=='__main__':
    # 測試用數據
    data = ['test', 'apple', 'banana', 'cat', 'dog', 'egg', 'fish', 'goat', 'house', 'ice', 'juice', 'kite', 'lemon', 'mango', 'noodle', 'orange', 'peach', 'queen', 'rice', 'sugar', 'tea', 'umbrella', 'violet', 'water', 'xenon', 'yogurt', 'zebra']
    # print(search('crazy', data)) # [('apple', 80)]

    # 中文測試數據
    chinese_data = ['黃子佼近況曝光！男星說出「關鍵人名」 秒被打斷好吃好秒被打斷好吃好秒被打斷好吃好秒被打斷好吃好', '好好吃', '好開心', '好開門', '好開朗', '好開運', '好開車', '好開懷', '好開眼界', '好開心', '好開懷', '在說啥']
    print(fuzzy_search('黃子佼近', chinese_data))

    # 測試 srt_search
    course_data2 =['''這篇文章主要講述了如何在一個圖形的情境中對不同的人進行探索。它提到了一個名為BFS (Breadth First Search) 的算法，用於在圖形上搜尋不同的方向。它還提到了一個名為DFS (Depth First Search) 的算法，用於在圖形上搜尋深度。這兩種算法都是基於圖形上的路徑，並且可以在不同的情況下應用。

    在文章的最後，文章提到了一個問題：如果一個圖形中有一個循環，如果這個圖形對不同的人進行探索，是否會出現重複？這個問題涉及到圖形上的路徑。文章提到了一個方法，用於判斷是否存在重複，並且提供了一個範例，說明如何使用這個方法。

    總體而言，這篇文章探討了如何在圖形上搜尋不同的方向，並且提到了一個重要的問題：如果一個圖形對不同的人進行探索，是否會出現重複。這個問題涉及到圖形上的路徑，並且可以通過BFS和DFS算法來解決。
    ''', 'ㄐㄐ', '靠北']

    print(fuzzy_search('廣度優先搜尋', course_data2)[0][1])
