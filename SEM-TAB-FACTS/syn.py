import copy
import csv,json
from tqdm import tqdm
import random
import glob
import pandas as pd
from collections import defaultdict
from fill_in_template import *


header = ('id', 'annotator', 'position', 'question', 'table_file',
			'answer_coordinates', 'answer_text', 'aggregation', 'float_answer')

TSV_FOLDER = '/home/lzy/data/UFTR/sem-tab-fact/tsv/'


def normalize(table):
    for i in range(len(table)):
        for j in range(len(table[i])):
            table[i][j] = table[i][j].replace("\n"," ").replace("  ","")
    return table

def get_templates():
    path = "template.jsonl"
    all_tems = []
    with open(path) as f:
        line = f.readline()
        while line:
            all_tems.append(json.loads(line))
            line = f.readline()
    return all_tems

def find_pos(table):
    # print(table)
    d = {}
    i = 0
    for key in table:
        d["c"+str(i)] = key
        d["val_"+str(i)] = table[key]
        i+=1
    return d

def gen_feed(pos_d,placeholder):
    feed_dict = {}
    for key in placeholder:
        if key.startswith("c"):
            for item in placeholder[key]:
                feed_dict[item] = pos_d[item]
        else:
            l = len(placeholder[key])
            pos_set = set(pos_d[key])
            # print(len(pos_set))
            # print(len(pos_d[key]))
            if len(pos_set)!= len(pos_d[key]):
                raise RuntimeError
            sampled_values = random.sample(pos_d[key],l)
            for item,value in zip(placeholder[key],sampled_values):
                feed_dict[item] = value
    return feed_dict

def fill_in_template(tem,table,pd_table):
    placeholder = tem["placeholder"]
    pos_d = find_pos(table)
    try:
        feed_dict = gen_feed(pos_d,placeholder)
    except:
        print("fail to gen feed_dict...")
        return None
    #The base 'eq' func can have many sub-funcs such as count,max,min,hop ... Using these templates is enough for a good unsupervised performence on sem-tab-facts 
    if tem["logic"]["func"] in ["eq","str_eq"] and tem["logic"]["args"][0]["func"]=="max":
        try:
            return fill_in_eq_template(tem,feed_dict,pd_table,table)
        except:
            return None
    elif tem["logic"]["func"]=="greater":
        return fill_in_greater_template(tem,feed_dict)
    elif tem["logic"]["func"]=="less":
        return fill_in_less_template(tem,feed_dict)
    else:
        pass

def filter_blank(table):
    new_table = copy.deepcopy(table)
    for key in new_table:
        column = []
        for item in new_table[key]:
            if item!="":
                column.append(item)
        new_table[key] = column
    return new_table

def rm_comma(content):
    for i in range(len(content)):
        for j in range(len(content[0])):
            content[i][j] = content[i][j].replace(',', '')

if __name__ == "__main__":
    train_files = sorted(glob.glob('/home/lzy/data/UFTR/sem-tab-fact/csv/train_man_*.csv'))
    print(len(train_files))
    succ_cnt = 0
    all_samples = []
    for i in range(len(train_files)):
        if i%10==0:
            print(i)
        file = open(train_files[i])
        table = list(csv.reader(file,delimiter=","))
        table = normalize(table)
        table_header = table[0]
        table_cont = table[1:]
        pd_in = defaultdict(list)
        for ind, header in enumerate(table_header):
            for inr, row in enumerate(table_cont):
                pd_in[header].append(row[ind])
        try:
            pd_table = pd.DataFrame(pd_in)
        except Exception as e:
            print("error")
            print(e)
            continue
        templates = get_templates()
        repeat = 10
        for r in range(repeat):
            valid_table = copy.deepcopy(pd_in)
            for tem in templates:
                fill_res = fill_in_template(tem,valid_table,pd_table)
                if fill_res!=None:
                    logic_str_support,logic_str_refute,must_have,must_have_wa,feed_dict = fill_res
                    all_samples.append({"topic":"none","sent":"none","interpret":"none","table_header":table_header,"table_cont":table_cont,"table_file":train_files[i].split("/")[-1],"logic_str":logic_str_support,"label":True,"must_have":must_have,"type":tem["type"]})
                    all_samples.append({"topic":"none","sent":"none","interpret":"none","table_header":table_header,"table_cont":table_cont,"table_file":train_files[i].split("/")[-1],"logic_str":logic_str_refute,"label":False,"must_have":must_have_wa,"type":tem["type"]})
                    succ_cnt+=1
                    # print(all_samples)
                    # exit(0)
    out_f = open("no_use.json",'w')
    out_f.write(json.dumps(all_samples))
    out_f.close()
    print("succ_cnt",succ_cnt)