import json

all_ops = ["subtract","divide","add","multiply","greater","exp","table_max","table_min","table_sum","table_average"]

def find_num(program):
    for op in all_ops:
        program = program.replace(op,"")
    program = program.replace("(","").replace(")","")
    all_nums = []
    for num in program.split(","):
        if not num.strip().startswith("#") and not num.strip().startswith("const"):#0丢弃,const丢弃
            all_nums.append(num.strip())
    return all_nums

def locate_num(num,table):
    for i in range(1,len(table)):
        for j in range(1,len(table[i])):
            if num in table[i][j]:
                return i,j
    return None,None

def get_description(num,table):
    # sen_located = None
    # for evi in evidences:
    #     if num in evi:
    #         sentences = evi.split(";")
    #         for sen in sentences:
    #             if num in sen:
    #                 sen_located = sen
    #                 break
    # if not sen_located:
    #     return None
    # des,_ = sen_located.split(" is ")[0],sen_located.split(" is ")[1]
    row_ind,col_ind = locate_num(num,table)
    if not row_ind:
        print("not found"+num)
        return None
    row_name = table[row_ind][0]
    col_name = table[0][col_ind]
    des = "the "+row_name+" of "+col_name
    return des.strip()

def revise(program,table):
    nums = find_num(program)
    # print(nums)
    verbalize = {}
    for num in nums:
        if num.startswith("const"):
            continue
        des = get_description(num,table)
        if des == None:
            return None
        verbalize[num]= des
    # print(verbalize)
    program = program.replace("("," ( ")
    program = program.replace(")"," ) ")
    print(verbalize)
    for key,value in verbalize.items():
        program = program.replace(key,value)    
    return program

def collect(input_path,out_f):
    data = json.load(open(input_path))
    print(len(data))
    succ = 0
    fail = 0
    for i in range(len(data)):
        nl = data[i]["qa"]["question"]
        program = data[i]["qa"]["program"]
        model_input = data[i]["qa"]["model_input"]
        table = data[i]["table"]
        # print(table)
        program = revise(program,table)
        # evidences = []
        # for item in model_input:
        #     if item[0].startswith("table"):
        #         evidences.append(item[1])
        # program = revise(program,evidences)
        # print(program)
        # print(nl)
        if program != None:
            succ+=1
            out_f.write(json.dumps({"program":program,"nl":nl})+"\n")
        else:
            fail+=1
    print("succ:",succ)
    print("fail:",fail)

def split_train_dev(input_f):
    all_samples = []
    train_path = "../dataset/train_op2nl.json"
    dev_path = "../dataset/dev_op2nl.json"
    with open(input_f) as f:
        for line in f:
            all_samples.append({"translation":json.loads(line)})
    print(len(all_samples))
    train_samples = all_samples[:int(len(all_samples)*0.9)]
    dev_samples = all_samples[int(len(all_samples)*0.9):]
    print(len(train_samples))
    print(len(dev_samples))
    with open(train_path,"w") as f:
        for sample in train_samples:
            f.write(json.dumps(sample)+"\n")
    with open(dev_path,"w") as f:
        for sample in dev_samples:
            f.write(json.dumps(sample)+"\n")
    
if __name__ == '__main__':
    out_path = "../dataset/syn.json"
    out_f = open(out_path,"w")
    input_path = '../dataset/train.json'
    collect(input_path,out_f)
    input_path = '../dataset/dev.json'
    collect(input_path,out_f)
    out_f.close()
    split_train_dev(out_path)