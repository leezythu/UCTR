import json
import pandas as pd
import os
import sqlite3
import random
import numpy as np
import copy
from my_utils import *

Types = [
    "word matching",
    # "sub",
    # "add",
    # "count",
    "compare",
    "spans"
]
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

def header(data):
    flag = True
    if data[0]!="":
        flag = False  
    for i in range(1,len(data)):
        if data[i]=="":
            flag = False
    return flag 

def midheader(data):
    flag = True
    if data[0]=="":
        flag = False  
    for i in range(1,len(data)):
        if data[i]!="":
            flag = False
    return flag     

def aggregate_header(table):
    index = None
    for i in range(len(table)):
        if header(table[i]):
            index = i
            # break 
    if index == None:
        return index
    if index>3:
        print("error,find wrong index")
        index = None
        print(table)
        return index
    for j in range(len(table[0])):
        for i in range(1,index+1):
            if table[i][j] != "":
                table[0][j] += " "+table[i][j]
        table[0][j] = table[0][j].strip()
    del table[1:index+1]
    return index

def find_midheader_index(table):
    indexs = []
    for i in range(len(table)):
        if midheader(table[i]):
            indexs.append(i)
    return indexs

def split_table(table,header_index,midheader_index):
    tables = []
    meta_info = table[:header_index+1]
    if len(midheader_index)>0:
        for index in midheader_index:
            for i in range(1,len(table[index])):
                table[index][i] = table[header_index][i]
        for i in range(len(midheader_index)-1):
            tables.append(table[midheader_index[i]:midheader_index[i+1]])
        tables.append(table[midheader_index[-1]:])
    else:
        tables.append(table[header_index:])
    return tables,meta_info

def sample_command(c,table,table_name,all_commands,type):
    res_list = []
    cnt = 0
    while True :
        cnt+=1
        if cnt>100:
            print("cannot sample valid command")
            print(table)
            print(command)
            return None,None
        command = copy.deepcopy(random.choice(all_commands[type]))
        if "w" not in command[0]:
            continue
        # command = [['select', 'c1', 'from', 'w', 'where', 'c2', '=', '5', 'order', 'by', 'c4', 'limit', '1'], 'which team was the first to have five winners ?', {'c1': {'c_idx': [1], 'val_idx': []}, 'c2': {'c_idx': [5], 'val_idx': [7]}, 'c4': {'c_idx': [10], 'val_idx': [12]}}]
        if "order by c1" in " ".join(command[0]):
            continue
        command = fit_command_for_table(table,command)
        if command == None:
            continue
        for i in range(len(command)):
            if command[i] == "w":
                command[i] = table_name
        command = " ".join(command)
        if "limit" in command and "limit 1" not in command:
            continue
        if "None" in command:
            continue
        if "[]" in command:
            continue
        try:
            res = c.execute(command)
        except:
            print("execute error")
            print("command",command)
            print("table:",table)
            continue
        res_list = [item[0]for item in res]
        if len(res_list) == 0:
            continue
        if None in res_list:
            continue
        if len(res_list)==1 and res_list[0]==0:
            continue
        for i in range(len(res_list)):
            if isinstance(res_list[i],float):
                res_list[i] = round(res_list[i],2) 
        break
    return command,res_list

def normalize_table(ori_table):
    table = copy.deepcopy(ori_table)
    max_number = -1e6
    for i in range(1,len(table)):
        for j in range(1,len(table[i])):
            table[i][j] = table[i][j].replace('%', '').strip()
            table[i][j] = table[i][j].replace('$', '').strip()
            if "(" in table[i][j] and ")" in table[i][j]:
                table[i][j] = table[i][j].replace('(', '')
                table[i][j] = table[i][j].replace(')', '')
                table[i][j] = "-"+table[i][j]
            try:
                table[i][j] = float(table[i][j].replace(",", ""))
                if table[i][j]>max_number:
                    max_number = table[i][j]
            except:
                table[i][j] = None
    return max_number,table
    

def normalize_table_2(table):
    for i in range(len(table)):
        for j in range(len(table[i])):
            table[i][j] = table[i][j].replace('%', '').strip()
            table[i][j] = table[i][j].replace('$', '').strip()
            if "(" in table[i][j] and ")" in table[i][j]:
                table[i][j] = table[i][j].replace('(', '')
                table[i][j] = table[i][j].replace(')', '')
                table[i][j] = "-"+table[i][j]
            try:
                if table[i][j] not in ["2017","2018","2019"]:
                    table[i][j] = float(table[i][j].replace(",", ""))
            except:
                pass

def generate_from(idx,table,all_commands,shift_index):
    if table[0][0]=="" or "2019" in table[0][0] or "2018" in table[0][0] or "2017" in table[0][0] :
        table[0][0] = "Items"
    headers = table[0][:]
    if "2019" in headers or "2018" in headers or "2017" in headers:
        if table[0][0]!="":
            table_caption = table[0][0]
        table[0][0]= "Years"
    test = pd.DataFrame(data=table)
    transpose_test = test.T
    table_name = "test"+str(idx)+"_transpose"
    transpose_test.to_csv(table_name+".csv",index=None,header=None)
    os.system("csvs-to-sqlite "+table_name+".csv -t "+table_name+" tat-tmp.db")
    conn = sqlite3.connect("tat-tmp.db")
    c = conn.cursor()
    syn_samples = []
    for type in Types:
        command,res_list = sample_command(c,transpose_test,table_name,all_commands,type)
        if command != None:
            command = command.replace(table_name,"w")
            syn_samples.append({"command":command,"res":res_list,"type":type})
    return syn_samples

def detect_scale(str,scale):
    if "in thousands" in str or "$'000" in str:
        scale.add("thousand")
    if "in millions" in str or "€m" in str:
        scale.add("million")
    if "in billions" in str:
        scale.add("billion")
    if "percent" in str or "%" in str:
        scale.add("percent")

def get_scale(table,para):
    scale = set()
    para_str = " ".join([item["text"] for item in para])
    table_str = ""
    for row in table:
        for item in row:
            table_str+=str(item)+" "
    # print(table_str)
    detect_scale(para_str.lower(),scale)
    detect_scale(table_str.lower(),scale)
    scale = list(scale)
    if "percent" in scale and "$" in table_str:
        scale.append("mixed percent and dollar")
    if len(scale) == 0:
        scale.append("")
    return scale
        
def drop_unuseful_info(table):
    for i in range(len(table)):
        for j in range(len(table[i])):
            if "in thousand" in table[i][j].lower() or "in million" in table[i][j].lower() or "in billion" in table[i][j].lower() or table[i][j].lower().startswith("year end"):
                table[i][j] = ""
            table[i][j] = table[i][j].replace('%', '')
            table[i][j] = table[i][j].replace('$', '')
            table[i][j] = table[i][j].replace(':', '')

def find_mapping(table,r):
    if r in [2017,2018,2019]:
        r = str(r)
    for i in range(len(table)):
        for j in range(len(table[0])):
            if table[i][j] == r:
                return i,j
    return None

def make_instance(processed_table,original_table,syn_q,scale):
    questions = []
    for item in syn_q:
        answer = set()
        mapping = {"table":[]}
        # print(item)
        try:
            for res in item["res"]:
                row,column = find_mapping(processed_table,res)
                mapping["table"].append([row,column])
        except:
            continue
        for index in mapping["table"]:
            answer.add(original_table[index[0]][index[1]])
        answer = list(answer)
        derivation = ""
        answer_type = item["type"]
        if answer_type == "word matching" or answer_type == "spans":
            if len(answer)==1:
                answer_type = "span"
            elif len(answer )>1:
                answer_type = "multi-span"
            else:
                print("res is none")
                print(item)
                exit(0)
        r,c = mapping["table"][0]
        _scale = ""
        if r != 0 and c!=0:
            try:
                number = float(item["res"][0])
                _scale = scale[0]
            except:
                pass

        answer_from = "table"
        facts = answer
        rel_paragraphs =  []
        req_comparison = False
        questions.append({
        "uid":None,
        "question":item["command"],
        "answer":answer,
        "scale": _scale,
        "mapping":mapping,
        "derivation":derivation,
        "answer_type":answer_type,
        "answer_from":answer_from,
        "facts":facts,
        "rel_paragraphs":rel_paragraphs,
        "req_comparison":req_comparison
        })
    return questions
        

if __name__ == "__main__":
    input_f = open("../tatqa/dataset_tagop/tatqa_dataset_all.json")
    all_commands = get_commands()
    samples = json.load(input_f)
    fail_cnt = [0,0,0,0]
    syn_samples = []
    for i in range(len(samples)):
        sample = samples[i]
        paras = sample["paragraphs"]
        table = copy.deepcopy(sample["table"]["table"])

        scale = get_scale(table,paras)
        if len(scale)>1:
            fail_cnt[0]+=1
            continue
        if scale[0]=="":
            fail_cnt[1]+=1
            continue

        original_table = copy.deepcopy(table)
        drop_unuseful_info(table)
        processed_table = copy.deepcopy(table)
        
        normalize_table_2(processed_table)
        ori_header_index = aggregate_header(table)
        if ori_header_index==None:
            fail_cnt[2]+=1
            continue
        header_index = 0
        midheader_index = find_midheader_index(table)
        sub_tables,meta_info = split_table(table,header_index,midheader_index)
        if len(midheader_index)==0:
            midheader_index = [0]

        idx = 0
        questions = []
        for mid_index,sub_table in zip(midheader_index,sub_tables):
            shift_index = ori_header_index+mid_index
            max_number,new_table = normalize_table(sub_table)
            if scale[0]=="percent" and max_number>100:
                print("not pure percent scale...")
                continue
            syn_q = generate_from(idx,new_table,all_commands,shift_index)
            qs = make_instance(processed_table,original_table,syn_q,scale)
            questions.extend(qs)
            idx += 1
        sample["questions"] = questions
            
        syn_samples.append(sample)
        try:
            os.system("rm tat-tmp.db")
        except:
            pass
    syn_out = open("syn_out.json",'w')
    syn_out.write(json.dumps(syn_samples))