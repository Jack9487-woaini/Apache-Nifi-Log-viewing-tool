from flask import Flask, render_template, jsonify, request
from tailer import follow
from threading import Thread, Lock
from collections import deque
import time

app = Flask(__name__)

log_deques = {
    'app' : deque(maxlen=100),  # Max size 100 double-ended queue
    'bootstrap' : deque(maxlen=100),  
    'deprecation' : deque(maxlen=100),  
    'request' : deque(maxlen=100),  
    'user' : deque(maxlen=100) 
}
log_files = {
    'app': r'your-file-path\nifi-app.log',
    'bootstrap': r'your-file-path\nifi-bootstrap.log',
    'deprecation': r'your-file-path\nifi-deprecation.log',
    'request': r'your-file-path\nifi-request.log',
    'user': r'your-file-path\nifi-user.log'
}
# thread lock, Keep messages synchronized 
# 線程鎖，保持 data 同步
log_deque_locks = {key: Lock() for key in log_files} 
# Tracking log txt updating function
# 監聽 log 更新
def track_log_updates(log_key):
    if log_key == 'None':
        return None
    with open(log_files[log_key], 'r') as log_file:
        for line in follow(log_file):
            with log_deque_locks[log_key]:
                log_deques[log_key].append(line) # 加入 log 新增的內容到 dequeue，若超過 100 行時，捨棄前面第一行內容就會被丟棄
                                    # When new log entries are added to the deque, and once the number of log 
                                    # lines in the deque exceeds 100, the earliest (first line) log content will be discarded.
# start the thread to each file            
# 幫 track 每個 log 文件啟動線程
for key in log_files:
    print(key)
    thread = Thread(target=track_log_updates, args=(key,))
    thread.daemon = True
    thread.start()

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/get_logs')
def get_logs():
    # Convert dequeue contents into list
    # 將 dequeue 內容轉成 list
    
    req_key = request.args.get('log')
    log_key = req_key 
    # print('log key: ',log_key) # For test 
    
    # 回傳 json 格式的 log data 
    # Convert the log data into JSON format, And return it
      
    with log_deque_locks[log_key]:
        print('----Log Data----')
        print(log_deques[log_key])
        print('----Log Data----')
        return jsonify(list(log_deques[log_key]))

if __name__ == '__main__':
    app.run(debug=True)
