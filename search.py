"""
與搜尋相關的函式
"""

from fuzzywuzzy import fuzz

def search(query, data):
    """
    這個函式會回傳一個 list，裡面包含了所有符合的結果
    每個結果都是一個 tuple，包含了 (名稱, 相似度)
    接收兩個參數 query 和 data 分別代表使用者輸入的字串和要比對的資料
    """
    results = []
    for item in data:
        score = fuzz.ratio(query.lower(), item.lower())
        if score > 50:
            results.append((item, score))
    results.sort(key=lambda x: x[1], reverse=True) # 依照分數由高到低排序
    return results

# 測試用數據
data = ['test', 'apple', 'banana', 'cat', 'dog', 'egg', 'fish', 'goat', 'house', 'ice', 'juice', 'kite', 'lemon', 'mango', 'noodle', 'orange', 'peach', 'queen', 'rice', 'sugar', 'tea', 'umbrella', 'violet', 'water', 'xenon', 'yogurt', 'zebra']
print(search('crazy', data)) # [('apple', 80)]

# 中文測試數據
chinese_data = ['黃子佼近況曝光！男星說出「關鍵人名」 秒被打斷', '好好吃', '好開心', '好開門', '好開朗', '好開運', '好開車', '好開懷', '好開眼界', '好開心', '好開懷', '在說啥']
print(search('男星', chinese_data))
