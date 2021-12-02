import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import  RandomizedSearchCV
from time import time, sleep, strftime
import os
import pandas as pd
from getpass import getpass
from subprocess import Popen, PIPE

timestr = strftime("%Y%m%d-%H%M%S")
path = "flows/flows"+timestr+".csv"
password = getpass("Please enter your password: ")
proc1 = Popen(f"echo {password}".split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
# sudo requires the flag '-S' in order to take input from stdin
proc2 = Popen(f"sudo -S cicflowmeter -i wlp3s0 -c {path}".split(), stdin=proc1.stdout, stdout=PIPE, stderr=PIPE)

poll = proc2.poll()
if poll is None:
    print("Running")
else:
    print("NO")
count_rows = 0
drop_cols = ['src_ip', 'src_port', 'dst_ip', 'dst_port',
            'bwd_psh_flags','fwd_urg_flags', 'bwd_urg_flags','cwe_flag_count',
            'fwd_byts_b_avg','fwd_pkts_b_avg','fwd_blk_rate_avg',
            'bwd_byts_b_avg','bwd_pkts_b_avg','bwd_blk_rate_avg'
            ,'timestamp']

with open('encoding.sav', 'rb') as of:
    labels_rev = pickle.load(of)

labels = {v:k for k,v in labels_rev.items()}

with open('fixmodel1.sav','rb') as of:
    model = pickle.load(of)
sleep(5)
last_mod=os.path.getmtime(path)
while True:
    cur_mod = os.path.getmtime(path)
    if cur_mod - last_mod > 0:
        data = pd.read_csv(path)
        data = data.iloc[count_rows:,:]
        data = data.drop(drop_cols,axis=1)
        print(data.shape)
        output = model.predict(data)
        for value in output:
            print(labels[value])
        count_rows += data.shape[0]
        last_mod = cur_mod
    else:
        sleep(5)
