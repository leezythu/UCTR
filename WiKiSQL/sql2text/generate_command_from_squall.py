import json
import sqlite3

def fill_in_column(sql,columns,tbl):
    column_dict = {}
    for i in range(len(columns)):
        column_dict["c"+str(i+1)] = columns[i][0]
    sql = sql.split()
    for i in range(len(sql)):
        if sql[i].split("_")[0] in column_dict:
            sql[i] = "["+column_dict[sql[i].split("_")[0]]+"]"
        elif sql[i] == 'w':
            sql[i] = "["+tbl+"]"
        else:
            sql[i] = sql[i]
    sql = " ".join(sql)
    return sql

def multi_ans(res_list):
    if len(res_list) == 1:
        return False
    if res_list[0][0]==res_list[1][0]:
        return False
    return True

def match(res_list,tgt):
    tgt = tgt.replace("–","-").lower()
    for res in res_list:
        tmp = str(res[0]).replace("–","-").lower()
        if tmp in tgt or tgt in tmp:
            return True
    return False

def execute(samples,out_f):
    out = open(out_f,'w')
    conn = sqlite3.connect('mydb.db')
    c = conn.cursor()
    fail_cnt = 0
    for i in range(len(samples)):
        tbl = samples[i]['tbl']
        sql = samples[i]['sql']
        info = sql
        sql = " ".join(item[1] for item in sql)
        columns = samples[i]['columns']
        template = sql

        sql = fill_in_column(sql,columns,tbl)
        if " id " in sql:
            continue
        if "[]" in sql:
            continue
        try:
            cursor = c.execute(sql)
        except Exception as e:
            fail_cnt +=1
            continue

        tgt = samples[i]["tgt"]
        res_list = []
        for res in cursor:
            res_list.append(res)
        print("res_list",res_list,"tgt:",tgt)
        if match(res_list,tgt):
            print("true")
            pair = {}
            nl = samples[i]['nl']
            nl = " ".join(nl)
            pair['nt'] = samples[i]['nt']
            pair["template"] = template
            pair["nl"] = nl
            pair["res"] = res_list
            pair["info"] = info
            if " - " in pair["template"] or "!=" in pair["template"]:
                pair["type"] = "sub"
            elif " + " in pair["template"]:
                pair["type"] = "add"
            elif "count" in pair["template"]:
                pair["type"] = "count"
            elif "min" in pair["template"] or "max" in pair["template"] or "order" in pair["template"] :
                pair["type"] = "compare"
            elif multi_ans(pair["res"]):
                pair["type"] = "spans"
            else:
                pair["type"] = "word matching"
            out.write(json.dumps(pair)+"\n")
        else:
            print("false")
    print("fail_cnt:",fail_cnt)
    
def collect_csv(samples):
    tbls = set()
    for i in range(len(samples)):
        s = samples[i]
        tbl = s['tbl']
        tbls.add(tbl)
    return tbls

def process_csv(tbls):
    for tbl in tbls:
        print(tbl)
        input_f = open("Table-Pretraining/raw_dataset/wtq/csv/"+tbl.split("_")[0]+"-csv/"+tbl.split("_")[-1]+".tsv")
        out_f = open("all_tables/"+tbl+".tsv",'w')
        line = input_f.readline()
        while line:
            line = line.lower()
            out_f.write(line)
            line = input_f.readline()
            
    command_path = "insert_train_tsv.sh"
    out_f = open(command_path,'w')
    for tbl in tbls:
        path = "all_tables/"+tbl+".tsv"
        command = "csvs-to-sqlite "+path+" -t "+tbl+" mydb_tsv.db -s '\\t'"
        out_f.write(command+"\n")
    out_f.close()

def find_left_column(idx,info):
    for i in range(idx-1,-1,-1):
        if info[i][0]=="Column":
            return i

def generate_filtered_commands(out_f,filtered_f):
    f = open(out_f)
    filtered_f = open(filtered_f,'w')

    line = f.readline()
    while line:
        line = json.loads(line)
        nl = line["nl"]
        info = line["info"]
        type = line["type"]
        replace_info = {}

        sql = [item[1] for item in info]
        for i in range(len(sql)):
            if len(sql[i].split("_"))>1 and sql[i].startswith("c") :
                sql[i] = sql[i].split("_")[0]
        print(sql)

        if "c1" not in sql:
            line = f.readline()
            continue
        if "!=" in sql:
            line = f.readline()
            continue
        if "next" in nl or "after" in nl:
            line = f.readline()
            continue
        for idx,item in enumerate(info):
            if item[0]=='Column':
                column_name = item[1].split("_")[0]
                if column_name not in replace_info:
                    replace_info[column_name] = {"c_idx":[],"val_idx":[]}
                replace_info[column_name]["c_idx"].append(idx)
        for idx,item in enumerate(info):
            if item[0].startswith("Literal"):
                c_idx = find_left_column(idx,info)
                column_name = info[c_idx][1].split("_")[0]
                replace_info[column_name]["val_idx"].append(idx)

        print(replace_info)
        if type == "compare" and len(replace_info)==1:
            line = f.readline()
            continue
        filtered_command = {}
        filtered_command["template"] = sql
        filtered_command["nl"] = nl
        filtered_command["replace_info"] = replace_info
        filtered_command["type"] = type
        filtered_f.write(json.dumps(filtered_command)+"\n")
        line = f.readline()

input = json.load(open("squall.json"))
out_f = "all_commands.jsonl"
filtered_f = "filtered_commands.jsonl"
print(len(input))
train = input[:10000]
valid = input[10000:]
all_csv_ids = collect_csv(train)
# process_csv(all_csv_ids)
execute(train,out_f)
generate_filtered_commands(out_f,filtered_f)
