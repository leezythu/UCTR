import json
def step1():
    #step 1 extracts sqls from syn_out.json for inference
    input_f = open("syn_out.json")
    input = json.load(input_f)
    print(len(input))
    sqls = []
    for sample in input:
        questions = sample["questions"]
        for question in questions:
            sqls.append(question["question"])
    print(len(sqls))
    infer_f = open("sql2nl_tat.json",'w')
    for sql in sqls:
        d = {"text":sql,"summary":""}
        infer_f.write(json.dumps(d)+"\n")
    infer_f.close()

def step2():
    cnt = 0
    succ_cnt = 0
    #step 2 generate the final training file
    final_samples = []
    src_f = open("syn_out.json")
    src = json.load(src_f)
    predict_f = open("result_tat/generated_predictions.txt")
    for sample in src:
        questions = sample["questions"]
        filtered_q = []
        for question in questions:
            sql = question["question"]
            nl = predict_f.readline()
            if ">" in sql or "<" in sql:
                continue
            if "total" in nl:
                continue
            if len(nl)>107:
                continue
            succ_cnt += 1
            question["question"] = nl.strip()
            if question["answer_type"] == "compare":
                question["answer_type"] = "span"
            try:
                question["scale"] = question["scale"][0]
            except:
                pass
            filtered_q.append(question)
            print(sql)
            print(nl)
            print()
            cnt+=1
        sample["questions"] = filtered_q
        final_samples.append(sample)

    print(succ_cnt)
    with open("tat_samples_gen.json",'w') as f:
        f.write(json.dumps(final_samples))

if __name__ == '__main__':
    step1()
    step2()
