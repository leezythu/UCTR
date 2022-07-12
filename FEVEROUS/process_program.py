from cmath import log
import json

def find_pos(rows):
    d = {}
    #header
    for i in range(len(rows[0])):
        d[rows[0][i]] = "c"+str(i)
    #value
    for j in range(1,len(rows)):
        for i in range(len(rows[j])):
            if rows[j][i] not in d:
                d[rows[j][i]] = "val"+"_"+str(j)+"_"+str(i)
    return d

def paraphrase(func):
    if func in ["eq","not_eq","filter_eq","filter_not_eq","most_not_eq","all_not_eq","count","only","and","max","min","avg","sum","nth_max","nth_min",
        "argmax","argmin","nth_argmax","nth_argmin","round_eq","greater","less","diff","filter_greater",
        "filter_less","filter_greater_eq","filter_less_eq","filter_all","all_eq","all_greater","all_less",
        "all_greater_eq","all_less_eq","most_eq","most_greater","most_less","most_greater_eq","most_less_eq"]:
        return func
    elif func=="str_hop"or func == "num_hop":
        return "hop"
    elif func == "nth_argmax":
        return "nth_argmax"
    elif func=="str_eq" :
        return "eq"
    elif func == "all_str_eq":
        return "all_eq"
    elif func == "filter_str_eq":
        return "filter_eq"
    elif func == "filter_str_not_eq":
        return "filter_not_eq"
    elif func == "not_str_eq":
        return "not_eq"
    elif func == "most_str_eq":
        return "most_eq"
    elif func == "most_str_not_eq":
        return "most_not_eq"
    else:
        raise NotImplementedError("unknown func:",func)

def ds_arg(logic,all,pos_d):
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
            sub_str = ds_arg(args[i],all,pos_d)
            logic_str += sub_str
        else:
            all.append(args[i])
            if args[i] in pos_d:
                args[i] = pos_d[args[i]]
            logic_str += args[i]
        logic_str += postfix
    logic_str += "}"
    return logic_str
    
def generalize(data,pos_d):
    logic = data["logic"]
    all_args = []
    placeholder = []
    #替换logic
    logic_str = ds_arg(logic,all_args,pos_d)
    # print("all_args:",all_args)
    replace = {}
    for item in all_args:
        if item in pos_d:
            replace[item] = pos_d[item]
    #替换str
    # logic_str = data["logic_str"]
    for key in replace:
        # logic_str = logic_str.replace(key,replace[key])
        placeholder.append(replace[key])
    return logic,logic_str,placeholder

def aggregate_val(placeholder):
    res = {}
    res["c"] = []
    for item in placeholder:
        if item.startswith("c"):
            res["c"].append(item)
        else:
            val_column = "val_"+item.split("_")[-1]
            if val_column not in res:
                res[val_column]=[]
            res[val_column].append(item)
    return res

data_folder = "./"
data_path = data_folder + "all_data.json"
out_path = data_folder+"template.jsonl"
out = open(out_path,'w')
with open(data_path) as f:
    data_in = json.load(f)

all_progs = []
for i in range(len(data_in)):
    data = data_in[i]
    table_header = data["table_header"]
    table_cont = data["table_cont"]
    table_rows = [table_header]+table_cont
    # print(table_rows)
    d = find_pos(table_rows)
    # print(d)
    interpret = data["interpret"]
    logic,logic_str,placeholder = generalize(data,d)
    placeholder = aggregate_val(placeholder)
    # if logic["func"] in ["eq"]:  
    # if "count" in logic_str:
    #     type = "count"
    # else :
    #     type = "eq"
    out.write(json.dumps({"logic_str":logic_str,"logic":logic,"interpret":interpret,"placeholder":placeholder,"type":type})+"\n")
out.close()