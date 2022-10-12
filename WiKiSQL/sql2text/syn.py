import json
from matplotlib.pyplot import LinearLocator
from more_itertools import numeric_range
import pandas as pd
import os
import random
import numpy as np
import copy
import records

Categorys = [
    "word matching",
    "sub",
    "add",
    "count",
    "compare",
    "spans"
]
category = "compare"

def get_commands():
    all_commands = {
        "word matching" : [],
        "spans" : [],
        "compare":[],
        "count":[],
        "add":[],
        "sub":[]
        }
    file = open("filtered_commands.jsonl")
    line = file.readline()
    while line:
        command = json.loads(line)
        all_commands[command["type"]].append([command["template"],command["nl"],command["replace_info"]])
        line = file.readline()
    return all_commands

def fit_command_for_table(table,command):
    must_have = []
    col_name,col_values = table["col_name"],table["col_values"]
    c_str,info = command[0],command[2]
    exe_str = copy.deepcopy(c_str)
    for key in info:
        c_idx,val_idx = info[key]["c_idx"],info[key]["val_idx"]
        for i in c_idx:
            c_str[i] = "["+col_name[key]+"]"
            index = int(key.replace("c",""))-1
            exe_str[i] = "col"+str(index)
        random_vals = random.sample(col_values[key],len(val_idx))
        cnt = 0
        for i in val_idx:
            c_str[i] = "["+random_vals[cnt]+"]"
            exe_str[i] = "'"+random_vals[cnt]+"'"
            must_have.append(str(random_vals[cnt]))
            cnt+=1
    return c_str,exe_str,must_have

def revise(command):
    new_command = []
    sql = []
    d = {}
    for val in command[0]:
        if val=="c1":
            sql.append("c3")
        else:
            sql.append(val)
    new_command.append(sql)
    new_command.append(command[1])
    for key in command[2]:
        if key=="c1":
            d["c3"] = command[2][key]
        else:
            d[key] = command[2][key]
    new_command.append(d)
    return new_command

def sample_command(c,table,table_id,all_commands,type,diverse_col):
    res_list = []
    cnt = 0
    while True :
        cnt+=1
        if cnt>100:
            print("cannot sample valid command")
            print(command)
            return None,None,None
        command = copy.deepcopy(random.choice(all_commands[type]))

        if diverse_col:
            assert "c1" in command[0]
            if "c2" in command[0]:
                continue
            command = revise(command)

        if command[0]==['select', 'count', '(', 'distinct', 'c1', ')', 'from', 'w'] or command[0]==['select', 'count', '(','c1', ')', 'from', 'w']: #too simple
            continue
        if "w" not in command[0] or "order by c1" in " ".join(command[0]) or "c1 <" in " ".join(command[0]) or "c1 >" in " ".join(command[0]):#
            continue
        if type=="word matching" or type == "count":
            if  ">" in " ".join(command[0]) or "<" in " ".join(command[0]) or "max" in " ".join(command[0]) or "min" in " ".join(command[0]) or "*" in " ".join(command[0]):
                continue
        try:
            command,exe_command,must_have = fit_command_for_table(table,command)
        except:
            continue
        if exe_command == None:
            continue
        for i in range(len(exe_command)):
            if exe_command[i] == "w":
                exe_command[i] = table_id
        exe_command = " ".join(exe_command)
        command = " ".join(command)
        if "limit" in command and "limit 1" not in command:#
            continue
        if "None" in command or "group by" in command:
            continue
        if "[]" in command:
            continue
        try:
            records = c.query(exe_command)
        except:
            print("execute error")
            print("command",command)
            continue
        res_list = []
        for res in records :
            res_list += list((res.as_dict().values()))
        if len(res_list)>=3:
            continue
        if len(res_list) == 0:
            res_list = ["none"]
        if len(res_list)==1 and res_list[0]==0:
            continue
        try:
            if type=="count" and int(res_list[0])>5:
                continue
        except:
            pass
        for i in range(len(res_list)):
            if isinstance(res_list[i],float):
                res_list[i] = round(res_list[i],2) 
        break
    return command,res_list,must_have

def generate_from(table_id,table,all_commands):
    table_id = "table_{}".format(table_id.replace('-', '_'))
    db = records.Database("sqlite:///../Table-Pretraining/examples/raw_dataset/wikisql_syn/data/train.db")
    conn = db.get_connection()
    syn_samples = []
    # sample commands of each type
    if category == "span":
        command,res_list,must_have = sample_command(conn,table,table_id,all_commands,"word matching",diverse_col = False)
        if command != None:
            syn_samples.append({"command":command,"res":res_list,"must_have":must_have,"type":"span"})
    elif category == "compare":
        command,res_list,must_have = sample_command(conn,table,table_id,all_commands,"compare",diverse_col = False)
        if command != None:
            syn_samples.append({"command":command,"res":res_list,"must_have":must_have,"type":"compare"})
    elif category == "count":
        command,res_list,must_have = sample_command(conn,table,table_id,all_commands,"count",diverse_col = False)
        if command != None:
            syn_samples.append({"command":command,"res":res_list,"must_have":must_have,"type":"count"})
    else:
        pass
    return syn_samples


def contain_number(table,header_types):
    new_table = {"col_name":{},"col_values":{}}
    numerical_keys = []
    for i in range(len(header_types)):
        if header_types[i] == "real":
            key = "c"+str(i+1)
            new_table["col_name"][key] = table["col_name"][key]
            new_table["col_values"][key] = table["col_values"][key]
            numerical_keys.append(key)
    return numerical_keys,new_table

def convert(table):
    new_table = {}
    col_name = {}
    col_values = {}
    for i in range(len(table[0])):
        col_name["c"+str(i+1)] = table[0][i]
        col_values["c"+str(i+1)] = []
    for i in range(len(table[0])):
        for j in range(1,len(table)):
            col_values["c"+str(i+1)].append(table[j][i])
    new_table["col_name"] = col_name
    new_table["col_values"] = col_values
    return new_table

if __name__ == "__main__":
    input_f = open("../Table-Pretraining/examples/raw_dataset/wikisql_syn/data/train.tables.jsonl")
    syn_f = open("syn.jsonl",'w')
    all_commands = get_commands()
    fail_cnt = [0,0,0,0]
    syn_samples = []
    line = input_f.readline()
    while line:
        sample = json.loads(line)
        table_id = sample["id"]
        header = sample["header"]
        header_types = sample["types"]
        rows = sample["rows"]
        table = [header]+rows
        pd_table = pd.DataFrame(data=table)
        table = convert(table)
        if category=="compare":
            numerical_keys,table = contain_number(table,header_types)
            if len(numerical_keys)<2:
                line = input_f.readline()
                continue
        syn_q = generate_from(table_id,table,all_commands)
        if len(syn_q)!=0:
            syn_sample = {"phase": 1,"table_id": table_id,"question":syn_q}
            syn_f.write(json.dumps(syn_sample)+"\n")
        line = input_f.readline()