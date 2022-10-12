from cmath import log
from process_program import paraphrase
from execution.execute import Node
import random

def ds_arg(logic,feed_dict):
    logic_str = ""
    logic_str += paraphrase(logic["func"])
    logic_str += " { "
    args = logic["args"]
    for i in range(len(args)):
        if i == len(args)-1:
            postfix = " "
        else:
            postfix = " ; "
        if isinstance(args[i],dict):
            sub_str = ds_arg(args[i],feed_dict)
            logic_str += sub_str
        else:
            if args[i] in feed_dict:
                args[i] = feed_dict[args[i]]
            logic_str += args[i]
        logic_str += postfix
    logic_str += "}"
    return logic_str

def find_index(val,table):
    for i in range(len(table)):
        for j in range(len(table[i])):
            if table[i][j] == val:
                return i,j

def get_evidence(feed_dict,must_have,type,table_index,doc,table,is_header):
    evidences = []
    evidence = {}
    evidence["content"] = []
    if type == "count":
        columns = []
        for key in feed_dict:
            if key.startswith("c"):
                columns.append(key.replace("c",""))
        for column in columns:
            for i in range(1,len(table)):
                if is_header[i][int(column)]:
                    evidence["content"].append(doc+"_header_cell_"+str(table_index)+"_"+str(i)+"_"+column)
                else:
                    evidence["content"].append(doc+"_cell_"+str(table_index)+"_"+str(i)+"_"+column)
    elif type == "row2text":
        for val in must_have:
            r_index,c_index = find_index(val,table)
            if is_header[r_index][c_index]:
                evidence["content"].append(doc+"_header_cell_"+str(table_index)+"_"+str(r_index)+"_"+str(c_index))
            else:
                evidence["content"].append(doc+"_cell_"+str(table_index)+"_"+str(r_index)+"_"+str(c_index))
    else:
        raise NotImplementedError("only implement count and row2text now")
    evidence["context"] = {}
    evidences.append(evidence)
    return evidences

def fill_in_eq_template(tem,feed_dict,pd_table,table):
    arg1 = tem["logic"]["args"][0]
    arg2 = tem["logic"]["args"][1]

    logic_str = ds_arg(arg1,feed_dict)
    
    res = Node(pd_table,arg1).eval()
    print("arg1_res:",res)
    if res == "":
        return None
    print(tem["type"])
    logic_str_support = "eq { "+logic_str+" ; "+str(res)+" }"
    if tem["type"] == "count":
        if random.random()>0.5:
            wa = res+1
        else:
            wa = res-1
        logic_str_refute = "eq { "+logic_str+" ; "+str(wa)+" }"
    elif tem["type"] == "row2text":
        column_index= int(arg2.split("_")[-1])
        values = table[list(table.keys())[column_index]]
        values.remove(res)
        if len(values)==0:
            return None
        wa = random.choice(values)
        logic_str_refute = "eq { "+logic_str+" ; "+str(wa)+" }"
    must_have = set()
    feed_dict[arg2] = res
    for key in feed_dict:
        if not key.startswith("c"):
            must_have.add(feed_dict[key])
    must_have_wa = set()
    feed_dict[arg2] = wa
    for key in feed_dict:
        if not key.startswith("c"):
            must_have_wa.add(feed_dict[key])
    return [logic_str_support,logic_str_refute,list(must_have),list(must_have_wa),feed_dict]
