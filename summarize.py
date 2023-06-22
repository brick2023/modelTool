'''
這個 module 主要包含和模型輸出相關的 function
請看清楚 function 使用方法再使用
注意：因為目前硬體資源問題，載入時間可能會有點久這是正常的喔 by yenslife
也可能因為記憶體不足而被 killed，目前難點卡在 token 的數量上限和硬體資源不足

requirement:
pip install transformers
pip install fschat 
'''

# TODO: 計算 token 數量，並處理異常 case

from transformers import AutoModelForCausalLM, AutoTokenizer
from fastchat.serve.inference import generate_stream 
from .fontcolor import bcolors
import time
import os

info_path = '/home/brick/yenslife/modelTool/test-text-data/information-short.txt'
format_path = '/home/brick/yenslife/modelTool/train-format.json'
vicuna_7b_model_path = "/home/brick/yenslife/model/vicuna-7b/"
# vicuna_13b_model_path = 'yenslife/vicuna-13b' # 在 huggingface 上面的

def load_model(model_path=vicuna_7b_model_path, low_cpu_mem_usage=True):
    print(f'正在載入模型 from {model_path}，可能需要等一下喔...')
    start_time = time.time()
    model = AutoModelForCausalLM.from_pretrained(model_path, low_cpu_mem_usage=low_cpu_mem_usage)
    print('模型載入完成')
    end_time = time.time()
    print(f"{model_path} loading time: ", end_time - start_time) # 計算 load tokenizer 和 model 的時間
    return model

def load_tokenizer(tokenizer_path=vicuna_7b_model_path, use_fast=True):
    print(f'正在載入 tokenizer(約 100 秒)...')
    start_time = time.time()
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, use_fast=use_fast)
    print('tokenizer載入完成')
    end_time = time.time()
    print(f' tokenizer loading time: ', end_time - start_time)
    return tokenizer

def text_to_summary(text, model_path=vicuna_7b_model_path, temperature=0.7):
    '''
    函式樣式：text_to_summarize(text, model_path=vicuna_13b_model_path, temperature=0.7)
    將一串文字作大意總節
    預設 model 為 vicuna-13b, temperature = 0.7 (可視情況做調整)
    '''

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
    
    # 載入 tokenizer
    tokenizer = load_tokenizer(model_path)

    # 計算文字長度、token 長度，以利 debug
    input_len = len(prompt)
    prompt_token_count = len(tokenizer.tokenize(prompt))
    print('prompt token 總數(超過 2000 有 crash 的風險):', prompt_token_count)
    if prompt_token_count > 2000:
        print(bcolors.WARNING + "警告：模型(13b)輸出可能出現無法預期的行為，因為 token > 2000 太多了，記憶體不堪負荷，目前還在想解決方案，拍謝" + bcolors.ENDC)

    # 載入模型
    model = load_model(model_path)

    # 喂給模型
    print('輸入資料到模型中...')
    gen_str = generate_stream(model, tokenizer, params, 'cpu', context_len=2048, stream_interval=2)
    final_text = ''

    for outputs in gen_str:
        output_text = outputs["text"]
        # print((output_text[input_len:]).replace('\n', ' '), flush=True, end="\r") # 這個目前輸出怪怪的，之後改
        # print(output_text[input_len:])
        if outputs['finish_reason'] == 'stop':
            final_text = output_text[input_len:]

    return final_text

def text_list_to_summary_list(text_list, model_path=vicuna_7b_model_path, temperature=0.7):
    """
    給定一個文字 list，輸出對應的 summary list
    函式樣式：text_to_summarize(text, model_path=vicuna_13b_model_path, temperature=0.7)
    將一串文字作大意總節
    預設 model 為 vicuna-13b, temperature = 0.7 (可視情況做調整)
    """

    # 載入 tokenizer
    tokenizer = load_tokenizer(model_path)

    # 載入模型
    model = load_model(model_path)

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
            print(bcolors.WARNING + "警告：模型(13b)輸出可能出現無法預期的行為，因為 token > 2000 太多了，記憶體不堪負荷，目前還在想解決方案，拍謝" + bcolors.ENDC)

        # 喂給模型
        print('輸入資料到模型中...')
        gen_str = generate_stream(model, tokenizer, params, 'cpu', context_len=2048, stream_interval=2)
        final_text = ''

        for outputs in gen_str:
            output_text = outputs["text"]
            # print((output_text[input_len:]).replace('\n', ' '), flush=True, end="\r") # 這個目前輸出怪怪的，之後改
            # print(output_text[input_len:])
            if outputs['finish_reason'] == 'stop':
                final_text = output_text[input_len:]

        return final_text
    
    summary_list = []
    for text in text_list:
        summary = summarizing(text)
        summary_list.append(summary)

    return summary_list

def file_text_dict_to_summary_files(file_text_dict, output_dir_path, model_path=vicuna_7b_model_path, temperature=0.7):
    """
    把 [檔案路徑]:[內容] 的 dict 喂給他，產生對應的 summary 檔案
    file_text_dict: [檔案路徑]:[內容]
    output_dir_path: 要把 summary 檔案放哪裡後面要加斜線喔，檔名為 file_text_dict 的檔名 e.g. './text-test/' 
    return output_dir_path
    """

    text_list = file_text_dict.values()
    summary_list = text_list_to_summary_list(text_list, model_path, temperature)

    for filepath in file_text_dict.keys():
        filename_with_extension = os.path.basename(filepath)
        filename = filename_with_extension.split('.')[0]
        summary = summary_list.pop(0)
        f = open(f'{output_dir_path}{filename}.txt', 'w')
        f.write(summary)
        f.close()

    return output_dir_path

def file_list_to_summary_dict(file_list, model_path=vicuna_7b_model_path, temperature=0.7):
    """
    給定一個檔案路徑 list，輸出對應的 summary dict 格式為 [檔名]:[摘要]
    函式樣式：text_to_summarize(text, model_path=vicuna_13b_model_path, temperature=0.7)
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
    summary_list = text_list_to_summary_list(text_list, model_path, temperature)

    # 包起來
    out_dict = dict()
    for file, summary in zip(file_list, summary_list):
        out_dict[file] = summary
    return out_dict

def file_list_to_summary_files(file_list, out_file_path, model_path=vicuna_7b_model_path, temperature=0.7):
    """
    給定一個檔案路徑 list，輸出對應的 summary 到指定檔案路徑
    函式樣式：text_to_summarize(text, model_path=vicuna_13b_model_path, temperature=0.7)
    將一串文字作大意總節
    預設 model 為 vicuna-13b, temperature = 0.7 (可視情況做調整)
    """
    # 取得 [path]:[summary]
    summary_dict = file_list_to_summary_dict(file_list, model_path, temperature)

    # 寫入檔案
    for input_file_path, summary in summary_dict.items():
        filename_with_extension = os.path.basename(input_file_path)
        filename = filename_with_extension.split('.')[0]
        f = open(f'{out_file_path}/{filename}.txt', 'w')
        f.write(summary)
        f.close()

    return out_file_path

def text_to_summary_file(text, output_path='./summarize.txt', model_path=vicuna_7b_model_path, temperature=0.7):
    '''
    將文字摘要輸出到特定檔案
    參數一：text
    參數二：output_path
    參數三：model_path (預設 vicuna_13b_model_path)
    參數四：temperature (預設 0.7)
    '''
    
    summarize = text_to_summary(text, model_path, temperature)
    print(f'正在將摘要寫入{output_path}')
    f = open(output_path, 'w')
    f.write(summarize)
    f.close
    print(f'已寫入{output_path}')
    return output_path

def file_text_to_summary_text(filepath, model_path=vicuna_7b_model_path, temperature=0.7):
    '''
    函式樣式：file_text_summarize(filepath, model_path=vicuna_13b_model_path, temperature=0.7)
    讀取文字檔案，並輸出概要總結
    file path: 檔案路徑
    預設 model 為 vicuna-13b, temperature = 0.7 (可視情況做調整)
    '''

    f = open(filepath, 'r')
    text = f.read()
    f.close()
    summerize = text_to_summary(text, model_path, temperature)
    return summerize

def file_text_to_summary_file(input_path, output_path='./out.txt', model_path=vicuna_7b_model_path, temperature=0.7):
    '''
    函式樣式：file_text_summarize(filepath, model_path=vicuna_13b_model_path, temperature=0.7)
    讀取文字檔案，並輸出概要總結到指定路徑檔案
    主要吃兩個參數 input_path 和 output_path
    output_path 預設為 ./out.txt
    '''
    summarize = file_text_to_summary_text(input_path, model_path, temperature)
    f = open(input_path, 'w')
    f.write(summarize)
    f.close()
    print(f'已將摘要寫入 {output_path}')

