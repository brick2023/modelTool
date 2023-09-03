'''
這個 module 主要包含和模型輸出相關的 function
請看清楚 function 使用方法再使用
注意：因為目前硬體資源問題，載入時間可能會有點久這是正常的喔 by yenslife
如果用的是給定 list 系列的函式，優點是可以只 load 一次 model，缺點是我們的主機無法負荷
所以要使用 function 還是建議用 for 迴圈跑 text_to 系列的慢慢 load 就好（畢竟只是要取得後台資料，使用者不會有感官上的問題）
也可能因為記憶體不足而被 killed，目前難點卡在 token 的數量上限和硬體資源不足

requirement:
pip install transformers
pip install fschat 
'''

# TODO: 計算 token 數量，並處理異常 case

from transformers import AutoModelForCausalLM, AutoTokenizer
from fastchat.serve.inference import generate_stream 
from fastchat.model.model_adapter import (
    load_model,
    get_conversation_template,
    get_generate_stream_function,
)
# from .fontcolor import bcolors
import torch
import time
import os
import gc

info_path = '/home/brick/yenslife/modelTool/test-text-data/information-short.txt'
format_path = '/home/brick/yenslife/modelTool/train-format.json'
vicuna_7b_model_path = "lmsys/vicuna-7b-v1.5"
# vicuna_13b_model_path = 'yenslife/vicuna-13b' # 在 huggingface 上面的

def text_to_summary(text, model_path=vicuna_7b_model_path, temperature=0.7, tokenizer=None, model=None):
    '''
    函式樣式：text_to_summarize(text, model_path=vicuna_13b_model_path, temperature=0.7, tokenizer=None, model=None)
    將一串文字作大意總節
    輸入：text: str, model_path: str, temperature: float, tokenizer: AutoTokenizer, model: AutoModelForCausalLM
    如果有輸入 tokenizer 和 model，則會直接使用，不會再 load 一次
    預設 model 為 vicuna-13b, temperature = 0.7 (可視情況做調整)
    '''

    prompt = f'''
human: 請閱讀以下文章：
"""
{text}
"""
請在300個繁體中文字內，總結以上這篇文章

Assistant:這篇文章講述了'''

    # 定義輸入參數
    params = {
        "prompt": prompt,
        "temperature": temperature, # 隨機性，越靠近1越高越隨機
        "max_new_tokens": 1000,
        "stop": "==="
    }

    input_len = len(prompt)
   
    # 載入模型, tokenizer
    if model == None or tokenizer == None:
        model, tokenizer = load_model(model_path)
    else:
        print('使用給定的 model')

    # 檢查顯卡
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print('device:', device)

    # 喂給模型
    print('輸入資料到模型中...')
    gen_str = generate_stream(model, tokenizer, params, device, context_len=2048, stream_interval=2)
    final_text = ''

    for outputs in gen_str:
        output_text = outputs["text"]
        # print((output_text[input_len:]).replace('\n', ' '), flush=True, end="\r") # 這個目前輸出怪怪的，之後改
        # print(output_text[input_len:])
        if outputs['finish_reason'] == 'stop':
            final_text = output_text[input_len:]

    # 釋放記憶體
    del tokenizer # 釋放記憶體
    del model # 釋放記憶體
    gc.collect() # 釋放記憶體

    return final_text

def long_text_to_summary(long_text, model_path=vicuna_7b_model_path, temperature=0.7, tokenizer=None, model=None):
    '''
    函式樣式：long_text_to_summarize(long_text, model_path=vicuna_13b_model_path, temperature=0.7, tokenizer=None, model=None)
    將一串文字作大意總節
    輸入：long_text: str, model_path: str, temperature: float, tokenizer: AutoTokenizer, model: AutoModelForCausalLM
    如果有輸入 tokenizer 和 model，則會直接使用，不會再 load 一次
    預設 model 為 vicuna-13b, temperature = 0.7 (可視情況做調整)
    和 text_to_summary 的差別是，他會幫你把長文字切成短的，然後再 call text_to_summary 去做
    '''

    # 載入模型, tokenizer
    if model == None or tokenizer == None:
        model, tokenizer = load_model(model_path)
    else:
        print('使用給定的 model')

    # 計算文字長度、token 長度，準備分段
    prompt_token_count = len(tokenizer.tokenize(long_text))
    avg_paragraphs_per_segment = round(750/prompt_token_count * len(long_text))
    num_segments = round(len(long_text)/avg_paragraphs_per_segment)
    print('avg_paragraphs_per_segment:', avg_paragraphs_per_segment)

    # 將長文字分段
    start_idx = 0
    segments = []
    for i in range(num_segments):
        end_idx = start_idx + avg_paragraphs_per_segment
        segment = ''.join(long_text[start_idx:end_idx])
        segments.append(segment)
        start_idx = end_idx
    summary_total = ''
    for text in segments:
        summary = text_to_summary(text=text, model=model, tokenizer=tokenizer, temperature=temperature)
        print(summary)
        summary_total += summary

    # 若還是太長，再分段，直到只剩下一段
    if num_segments > 1:
        summary_total = long_text_to_summary(summary_total, model_path, temperature, tokenizer, model)

    return summary_total
        


def text_list_to_summary_list(text_list, model_path=vicuna_7b_model_path, temperature=0.7, tokenizer=None, model=None):
    """
    給定一個文字 list，輸出對應的 summary list
    函式樣式：text_list_to_summary_list(text_list, model_path=vicuna_7b_model_path, temperature=0.7, tokenizer=None, model=None)
    輸入：text_list: list, model_path: str, temperature: float, tokenizer: AutoTokenizer, model: AutoModelForCausalLM
    如果有輸入 tokenizer 和 model，則會直接使用，不會再 load 一次
    將一串文字作大意總節
    預設 model 為 vicuna-13b, temperature = 0.7 (可視情況做調整)
    """

    # 載入 tokenizer
    # if tokenizer == None:
    #     tokenizer = load_tokenizer(model_path)
    # else:
    #     print('使用給定的 tokenizer')

    # 載入模型, tokenizer
    if model == None or tokenizer == None:
        model, tokenizer = load_model(model_path)
    else:
        print('使用給定的 model')

    def summarizing(text):
        prompt = f'''
        human: 請閱讀以下文章：
        """
        {text}
        """
        請在300個繁體中文字內，總結以上這篇文章

        Assistant:
        '''

        # 定義輸入參數
        params = {
            "prompt": prompt,
            "temperature": temperature, # 隨機性，越靠近1越高越隨機
            "max_new_tokens": 1000,
            "stop": "==="
        }
    
        # 計算文字長度、token 長度，以利 debug
        input_len = len(prompt)
        prompt_token_count = len(tokenizer.tokenize(prompt))
        print('prompt token 總數(超過 2000 有 crash 的風險):', prompt_token_count)
        if prompt_token_count > 2000:
            print(bcolors.WARNING + f"警告：模型({model_path})輸出可能出現無法預期的行為，因為 token > 2000 太多了，記憶體不堪負荷，目前還在想解決方案，拍謝" + bcolors.ENDC)

        # 檢查顯卡
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print('device:', device)

        gen_str = generate_stream(model, tokenizer, params, device, context_len=2048, stream_interval=2)

        # 喂給模型
        print('輸入資料到模型中...')
        gen_str = generate_stream(model, tokenizer, params, device, context_len=2048, stream_interval=2)
        final_text = ''

        for outputs in gen_str:
            output_text = outputs["text"]
            if outputs['finish_reason'] == 'stop':
                final_text = output_text[input_len:]

        return final_text
    
    summary_list = []
    for text in text_list:
        summary = summarizing(text)
        summary_list.append(summary)

    if len(summary_list) == len(text_list):
        print('所有文章都已總結完成')
    else:
        print('有文章沒有總結完成，請檢查')

    # 釋放記憶體
    del model 
    del tokenizer
    gc.collect() # gc.collect() 會釋放記憶體，但是不會把變數刪掉，所以要 del 變數

    return summary_list

def file_text_dict_to_summary_files(file_text_dict, output_dir_path, model_path=vicuna_7b_model_path, temperature=0.7, tokenizer=None, model=None):
    """
    把 [檔案路徑]:[內容] 的 dict 喂給他，產生對應的 summary 檔案
    file_text_dict: [檔案路徑]:[內容]
    output_dir_path: 要把 summary 檔案放哪裡後面要加斜線喔，檔名為 file_text_dict 的檔名 e.g. './text-test/' 
    return output_dir_path
    """

    text_list = file_text_dict.values()
    summary_list = text_list_to_summary_list(text_list, model_path, temperature, tokenizer, model)

    for filepath in file_text_dict.keys():
        filename_with_extension = os.path.basename(filepath)
        filename = filename_with_extension.split('.')[0]
        summary = summary_list.pop(0)
        f = open(f'{output_dir_path}{filename}.txt', 'w')
        f.write(summary)
        f.close()

    return output_dir_path

def file_list_to_summary_dict(file_list, model_path=vicuna_7b_model_path, temperature=0.7, tokenizer=None, model=None):
    """
    給定一個檔案路徑 list，輸出對應的 summary dict 格式為 [檔名]:[摘要]
    函式樣式：text_to_summarize(text, model_path=vicuna_13b_model_path, temperature=0.7, tokenizer=None, model=None)
    將一串文字作大意總節
    預設 model 為 vicuna-13b, temperature = 0.7 (可視情況做調整)
    """
    
    # 讀檔
    text_list = []
    for file in file_list:
        f = open(file, 'r')
        text = f.read()
        f.close()
        text_list.append(text)

    # 取得摘要
    summary_list = text_list_to_summary_list(text_list, model_path, temperature, tokenizer, model)

    # 包起來
    out_dict = dict()
    for file, summary in zip(file_list, summary_list):
        out_dict[file] = summary
    return out_dict

def file_list_to_summary_files(file_list, out_file_path, model_path=vicuna_7b_model_path, temperature=0.7, tokenizer=None, model=None):
    """
    給定一個檔案路徑 list，輸出對應的 summary 到指定檔案路徑
    函式樣式：text_to_summarize(text, model_path=vicuna_13b_model_path, temperature=0.7, tokenizer=None, model=None)
    將一串文字作大意總節
    預設 model 為 vicuna-13b, temperature = 0.7 (可視情況做調整)
    """
    # 取得 [path]:[summary]
    summary_dict = file_list_to_summary_dict(file_list, model_path, temperature, tokenizer, model)

    # 寫入檔案
    for input_file_path, summary in summary_dict.items():
        filename_with_extension = os.path.basename(input_file_path)
        filename = filename_with_extension.split('.')[0]
        f = open(f'{out_file_path}/{filename}.txt', 'w')
        f.write(summary)
        f.close()

    return out_file_path

def text_to_summary_file(text, output_path='./summarize.txt', model_path=vicuna_7b_model_path, temperature=0.7, tokenizer=None, model=None):
    '''
    將文字摘要輸出到特定檔案
    參數一：text
    參數二：output_path
    參數三：model_path (預設 vicuna_13b_model_path)
    參數四：temperature (預設 0.7)
    參數五：tokenizer (預設 None)
    參數六：model (預設 None)
    '''
    
    summarize = text_to_summary(text, model_path, temperature, tokenizer, model)
    print(f'正在將摘要寫入{output_path}')
    f = open(output_path, 'w')
    f.write(summarize)
    f.close
    print(f'已寫入{output_path}')
    return output_path

def file_text_to_summary_text(filepath, model_path=vicuna_7b_model_path, temperature=0.7, tokenizer=None, model=None):
    '''
    函式樣式：file_text_summarize(filepath, model_path=vicuna_13b_model_path, temperature=0.7)
    讀取文字檔案，並輸出概要總結
    file path: 檔案路徑
    tokenizer: 預設 None
    model: 預設 None
    預設 model 為 vicuna-13b, temperature = 0.7 (可視情況做調整)
    '''

    f = open(filepath, 'r')
    text = f.read()
    f.close()
    summerize = text_to_summary(text, model_path, temperature, tokenizer, model)
    return summerize

def file_text_to_summary_file(input_path, output_path='./out.txt', model_path=vicuna_7b_model_path, temperature=0.7, tokenizer=None, model=None):
    '''
    讀取文字檔案，並輸出概要總結到指定路徑檔案
    主要吃兩個參數 input_path 和 output_path
    input_path: 輸入檔案路徑
    output_path: 輸出檔案路徑 (預設為 ./out.txt)
    tokenizer: 預設 None
    model: 預設 None
    '''
    summarize = file_text_to_summary_text(input_path, model_path, temperature, tokenizer, model)
    f = open(output_path, 'w')
    f.write(summarize)
    f.close()
    print(f'已將摘要寫入 {output_path}')

def introduction(keyword, model_path=vicuna_7b_model_path, temperature=0.5, tokenizer=None, model=None):
    """
    搜尋關鍵字，介紹關鍵字
    """
    prompt = f"human: 請用繁體中文簡單介紹一下{keyword}，如果要學習相關的知識，應該搜尋哪些關鍵字。assistant:"
    # 定義輸入參數
    params = {
        "prompt": prompt,
        "temperature": temperature, # 隨機性，越靠近1越高越隨機
        "max_new_tokens": 1000,
        "stop": "==="
    }

    # 載入模型, tokenizer
    if model == None or tokenizer == None:
        model, tokenizer = load_model(model_path)

    # 喂給模型
    print('輸入資料到模型中...')
    
    # 檢查顯卡
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print('device:', device)

    gen_str = generate_stream(model, tokenizer, params, device, context_len=2048, stream_interval=2)
    
    print('輸入資料到模型中...完成')

    # 釋放記憶體
    del tokenizer # 釋放記憶體
    del model # 釋放記憶體
    gc.collect() # 釋放記憶體
    return gen_str
    # return final_text

if __name__ == "__main__":
    # keyword = '珍珠奶茶'
    # gen_str = introduction(keyword=keyword)
    # for g in gen_str:
    #     print('genstr:', g['text'])

    # 將指定資料夾底下的文字檔案，做摘要總結，並輸出到指定資料夾
    input_dir_path = '/home/brick/platform/src/video-info/company1/algorithm/'
    output_dir_path = '/home/brick/platform/src/summary/company1/algorithm/'
    custom_url = f'http://brick2.yenslife.top:2023/long_text_to_summary' # http://140.116.82.218:2023
    
    file_list = [os.path.join(input_dir_path, file) for file in os.listdir(input_dir_path)] # 這邊是為了把檔案路徑變成 list
    for file in file_list:
        with open(file, 'r') as f:
            long_text = f.read()
        import urllib.request
        import requests
        summary = '' 
        # 向有顯卡的主機請求
        response = requests.post(custom_url, data={'text': long_text})
        summary = response.text
        print(summary)
        filename = os.path.basename(file)
        f = open(output_dir_path + filename, 'w')
        f.write(summary)
        f.close()