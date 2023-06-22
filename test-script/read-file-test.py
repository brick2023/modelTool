data_path = './speech.txt'
vicuna_model_path = "../model/vicuna-7b/"
f = open(data_path, 'r')
data = f.read()
input_text = "hello 可愛小羊駝！"
input_text = input_text + data
prompt = f"Human: 我會用三個反引號包住你需要的特定領域知識```{input_text}```請依照給定的資訊，產生可以 fine tune 的 json 資料格式。Assitant:"
input_len = len(prompt)
print(input_len)
print(prompt[input_len:])
