import json
import copy
import random

from sqlalchemy import false
cnt = 0
succ_cnt = 0
final_samples = []
predict_f = open("result_wikisql/generated_predictions.txt")

src_f = open("syn.jsonl")
out_f = open("train.jsonl",'w')
line = src_f.readline()
while line:
    line = json.loads(line)
    questions = line["question"]
    for question in questions:
        sample = copy.deepcopy(line)
        sql = question["command"]
        category = question["type"]
        must_have = question["must_have"]
        nl = predict_f.readline().lower()
        if category =="span" or category =="word matching":
            if ">" in sql or "<" in sql or "No." in sql:
                continue
            if "total" in nl or "how many" in nl or "difference" in nl:
                continue
            if len(must_have)==0:
                continue
        flag = True
        for have in must_have:
            if have not in nl.replace(" ",""):
                flag = False
        if not flag:
            continue

        if len(nl)>107:
            continue
        
        succ_cnt += 1
        if category == "count":
            if random.random()<0.5:
                nl = nl.replace("how many","what is the total number of")
        sample["question"] = nl.strip().replace("only","").replace("  "," ")
        sample["command"] = sql
        # sample["answer"] = question["res"]
        sample["answer"] = "none"
        out_f.write(json.dumps(sample)+"\n")
        print(sql)
        print(nl)
        print()
        cnt+=1
    line = src_f.readline()
print(succ_cnt)
