import json
input_f = open("syn.jsonl")
line = input_f.readline()
sqls = []
while line:
    line = json.loads(line)
    questions = line["question"]
    for question in questions:
        sqls.append(question["command"])
    line = input_f.readline()

infer_f = open("sql2nl_wikisql.json",'w')
for sql in sqls:
    d = {"text":sql,"summary":""}
    infer_f.write(json.dumps(d)+"\n")
infer_f.close()

