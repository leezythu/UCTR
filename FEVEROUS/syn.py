from src.feverous.database.feverous_db import FeverousDB
from src.feverous.utils.wiki_page import WikiPage
import random,json,re
from collections import defaultdict
import pandas as pd
from execution.execute import Node
from process_program import paraphrase
from fill_in_template import *
import copy

def normalize(row):
    row = row.cell_content
    for i in range(len(row)):
        item = row[i]
        res = re.findall(r".*(\[\[(.*)\|(.*)\]\]).*",item)
        if res!=[]:
            row[i] = item.replace(res[0][0],res[0][2])
    return row

def get_templates():
    path = "templates.jsonl"
    all_tems = []
    with open(path) as f:
        line = f.readline()
        while line:
            all_tems.append(json.loads(line))
            line = f.readline()
    return all_tems

def find_pos(table):
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
    if tem["logic"]["func"] in ["eq","str_eq"]:
        return fill_in_eq_template(tem,feed_dict,pd_table,table)
    #the compare type only occupies a small fraction of the feverous dataset
    # elif tem["logic"]["func"]=="greater":
    #     return fill_in_greater_template(tem,feed_dict)
    # elif tem["logic"]["func"]=="less":
    #     return fill_in_less_template(tem,feed_dict)
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

    db =  FeverousDB("data/feverous_wikiv1.db")
    with open("selected_docs.json") as f:
        docs = json.load(f)
    # print(len(docs))
    # exit(0)
    docs = docs[:200000]
    all_samples = []
    for i in range(len(docs)):
        if i%1000==0:
            print(i)
        doc = docs[i]
        # print(doc)
        page_json = db.get_doc_json(doc)
        wiki_page = WikiPage(doc, page_json)
        wiki_tables = wiki_page.get_tables()
        all_tables = wiki_tables
        current_page = wiki_page
        table_index = random.choice(range(1,len(wiki_tables)))
        table = wiki_tables[table_index]
        header_row = table.get_header_rows()
        if len(header_row) != 1:
            print("many header rows!!")
            continue
        header_content = table.get_rows()[0].cell_content
        header_content_set = set(header_content)
        if len(header_content_set)!=len(header_content):
            print("duplicate headers!")
            continue
        is_header = []
        for i,row in enumerate(table.get_rows()):
            is_header.append([])
            for cell in row.row:
                if cell.is_header:
                    is_header[i].append(True)
                else:
                    is_header[i].append(False)

        normalized_table = []
        for row in table.get_rows():
            row = normalize(row)
            normalized_table.append(row)
        
        if len(normalized_table)<=2 or len(normalized_table)>20:
            print("table is too small or large...")
            continue
        table_header = normalized_table[0]
        table_cont = normalized_table[1:]
        rm_comma(table_cont)
        pd_in = defaultdict(list)
        for ind, header in enumerate(table_header):
            for inr, row in enumerate(table_cont):
                pd_in[header].append(row[ind])
        try:
            pd_table = pd.DataFrame(pd_in)
        except Exception as e:
            continue
        valid_table = filter_blank(pd_in)
        templates = get_templates()
        for tem in templates:
            fill_res = fill_in_template(tem,valid_table,pd_table)
            if fill_res!=None:
                logic_str_support,logic_str_refute,must_have,must_have_wa,feed_dict = fill_res
                evidence = get_evidence(feed_dict,must_have,tem["type"],table_index,doc,normalized_table,is_header)
                all_samples.append({"topic":doc,"table_index":table_index,"sent":"none","interpret":"none","logic_str":logic_str_support,"table_header":table_header,"table_cont":table_cont,"label":True,"must_have":must_have,"evidence":evidence,"type":tem["type"]})
                all_samples.append({"topic":doc,"table_index":table_index,"sent":"none","interpret":"none","logic_str":logic_str_refute,"table_header":table_header,"table_cont":table_cont,"label":False,"must_have":must_have_wa,"evidence":evidence,"type":tem["type"]})

    out_f = open("gpt_base/data_folder/original_data/wiki_tems.json",'w')
    out_f.write(json.dumps(all_samples))
    out_f.close()
