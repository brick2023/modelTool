import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, LlamaTokenizer, AutoModel
from fastchat.serve.inference import generate_stream 
import time


info_path = './speech.txt'
format_path = './format.json'
vicuna_model_path = "../model/vicuna-13b/"
f = open(info_path, 'r')
information = f.read()
input_text = "在知識創造的章節，作者提到了 information (內化) 和 exformation (外化)。information 指的是從外部吸收資訊，並在心裡形成理解。在輸入新資訊後，將自己形塑成世界所要求的模樣；exformation 則是將心裡的理解在外界創新。除了輸出以外，也在這世界創造出自己想要的東西。要進行知識創造，exformation 不可或缺（畢竟都說是「創造」了），在發表之前自己就要先好好釐清資訊，並吸收他人的反饋，加深自己思考的深度，進入正向循環。"
#prompt = f'human: 請幫我分析用三個引號包住的內容，以下是內容：'''{input_text}'''。Assistant:'
#input_text = input_text + information
f = open(format_path, 'r')
format = f.read()
f.close()
prompt = f"Human:請參考以下 json 格式:\
'''\n{format}\n'''\n\
請使用以上的格式來對以下的資料作出範例 json 檔案：\n\
```\n{information}\n```\n\
Assistant:"
input_len = len(prompt)
print(f'input len: {input_len}')


print('timer start...')
print('loading...')
start_time = time.time()
tokenizer = AutoTokenizer.from_pretrained(vicuna_model_path, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(vicuna_model_path, low_cpu_mem_usage=True)
print('done loading.')
end_time = time.time()
print('time: ', end_time - start_time) # 計算 load tokenizer 和 model 的時間

params = {
    "prompt": prompt,
    "temperature": 0.2, # 隨機性，越靠近1越高
    "max_new_tokens": 1000,
    "stop": "==="
}

gen_str = generate_stream(model, tokenizer, params, 'cpu', context_len=4096, stream_interval=2)

# 這邊參考了原始碼中的 fastchat/serve/cli.py 的 class SimpleChatIO
final_text = ""
for outputs in gen_str:
    pre = 0
    output_text = outputs["text"]
    if outputs['finish_reason'] == 'stop':
        print('結束之前')
        print(output_text)
        final_text = output_text[input_len:]
        print("結束了")
    else:
        print(output_text[input_len:], flush=True, end="\r")

#final_text = final_text[input_len:]
print(f'Vicuna 產生的資料: {final_text}')
print("====end of line====")
