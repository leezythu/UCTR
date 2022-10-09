import random
import numpy as np
def drop_unuseful_info(table):
    for i in range(len(table)):
        for j in range(len(table[i])):
            if "in thousand" in table[i][j].lower() or "in million" in table[i][j].lower() or "in billion" in table[i][j].lower() or table[i][j].lower().startswith("year end"):
                table[i][j] = ""
            table[i][j] = table[i][j].replace('%', '')
            table[i][j] = table[i][j].replace('$', '')
            table[i][j] = table[i][j].replace(':', '')

def midheader(data):
    flag = True
    if data[0]=="":
        flag = False  
    for i in range(1,len(data)):
        if data[i]!="":
            flag = False
    return flag 

def find_midheader_index(table):
    indexs = []
    for i in range(len(table)):
        if midheader(table[i]):
            indexs.append(i)
    return indexs

def header(data):
    flag = True
    if data[0]!="":
        flag = False  
    for i in range(1,len(data)):
        if data[i]=="":
            flag = False
    return flag 


def aggregate_header(table):
    index = None
    for i in range(len(table)):
        if header(table[i]):
            index = i
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
    detect_scale(para_str.lower(),scale)
    detect_scale(table_str.lower(),scale)
    scale = list(scale)
    if "percent" in scale and "$" in table_str:
        scale.append("mixed percent and dollar")
    if len(scale) == 0:
        scale.append("")
    return scale

def normalize_table(table):
    max_number = -1e6
    #deal with numbers
    for i in range(1,len(table)):
        for j in range(1,len(table[i])):
            table[i][j] = table[i][j].replace('%', '')
            table[i][j] = table[i][j].replace('$', '')
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
    return max_number

def shift_index(table,sub_table):
    data_row_name = sub_table[1][0]
    for i in range(len(table)):
        if table[i][0]==data_row_name:
            return i-1
    print("error! cannot find shift index")
    exit(0)

def make_instance(question,answer,derivation,answer_type,answer_form,facts,mapping,rel_paragraphs,req_comparison,scale,sub_table_name="",program=""):
    return {
        "uid":None,
        "question":question,
        "answer":answer,
        "scale": scale,
        "mapping":mapping,
        "derivation":derivation,
        "program":program,
        "sub_table_name":sub_table_name,
        "answer_type":answer_type,
        "answer_from":answer_form,
        "facts":facts,
        "rel_paragraphs":rel_paragraphs,
        "req_comparison":req_comparison
    }

def syn_table_span(table,ori_table,shift_index,scale,return_program = False):
    if len(table)<=3:
        return None
    cnt = 0
    while True:
        cnt+=1
        if cnt>10:
            return None
        row_index = random.sample(range(1,len(table)),2)
        column_index = random.sample(range(1,len(table[0])),2)
        values = []
        for row,column in zip(row_index,column_index):
            values.append(table[row][column])
        valid_flag = True
        for value in values:
            if value == None:
                valid_flag=False
        if valid_flag:
            break
    questions = []
    for row,column in zip(row_index,column_index):
        value = ori_table[row][column]
        table_name = table[0][0]
        row_name = table[row][0]
        column_name = table[0][column]
        if random.random()<0.5:
            prefix = "What was the "
        else:
            prefix = "What is the "
        if table_name!="":
            question = prefix + row_name + " of "+column_name+" for "+table_name+"?"
        else:
            question = prefix + row_name + " of "+column_name+"?"
        answer = []
        answer.append(value)
        derivation = ""
        answer_type = "span"
        answer_form = "table"
        facts = answer
        mapping = {"table":[]}
        mapping["table"].append([row+shift_index,column])
        rel_paragraphs =  []
        req_comparison = False
        _scale = scale[0]
        questions.append(make_instance(question,answer,derivation,answer_type,answer_form,facts,mapping,rel_paragraphs,req_comparison,_scale))
    return questions


def syn_table_multi_span(table,ori_table,shift_index,scale,return_program = False):
    questions = []
    if len(table)<=3:
        return None
    cnt = 0
    while True:
        cnt+=1
        if cnt>10:
            return None
        row_index = random.choice(range(1,len(table)))
        column_index = random.sample(range(1,len(table[0])),2)
        values = []
        for column in column_index:
            values.append(table[row_index][column])
        valid_flag = True
        for value in values:
            if value == None:
                valid_flag=False
        if valid_flag:
            break
    value1 = ori_table[row_index][column_index[0]]
    value2 = ori_table[row_index][column_index[1]]
    table_name = table[0][0]
    row_name = table[row_index][0]
    column_name1 = table[0][column_index[0]]
    column_name2 = table[0][column_index[1]]
    prefix = "What are the "
    if table_name!="":
        question = prefix + row_name + " of "+column_name1+" and "+ column_name2 +" for "+table_name+" respectively?"
    else:
        question = prefix + row_name + " of "+column_name1+" and "+ column_name2+" respectively?"
    answer = []
    answer.append(value1)
    answer.append(value2)
    derivation = ""
    answer_type = "multi-span"
    answer_form = "table"
    facts = answer
    mapping = {"table":[]}
    mapping["table"].append([row_index+shift_index,column_index[0]])
    mapping["table"].append([row_index+shift_index,column_index[1]])
    rel_paragraphs =  []
    req_comparison = False
    _scale = scale[0]
    questions.append(make_instance(question,answer,derivation,answer_type,answer_form,facts,mapping,rel_paragraphs,req_comparison,_scale))
    cnt = 0
    while True:
        cnt+=1
        if cnt>10:
            return None
        row_index = random.sample(range(1,len(table)),2)
        column_index = random.choice(range(1,len(table[0])))
        values = []
        for row in row_index:
            values.append(table[row][column_index])
        valid_flag = True
        for value in values:
            if value == None:
                valid_flag=False
        if valid_flag:
            break
    value1 = ori_table[row_index[0]][column_index]
    value2 = ori_table[row_index[1]][column_index]
    table_name = table[0][0]
    column_name = table[0][column_index]
    row_name1 = table[row_index[0]][0]
    row_name2 = table[row_index[1]][0]
    prefix = "What are the "
    if table_name!="":
        question = prefix + row_name1 +" and " +row_name2+" of "+column_name + " in "+table_name+" respectively?"
    else:
        question = prefix + row_name1 +" and " +row_name2+" of "+column_name +" respectively?"
    answer = []
    answer.append(value1)
    answer.append(value2)
    derivation = ""
    answer_type = "multi-span"
    answer_form = "table"
    facts = answer
    mapping = {"table":[]}
    mapping["table"].append([row_index[0]+shift_index,column_index])
    mapping["table"].append([row_index[1]+shift_index,column_index])
    rel_paragraphs =  []
    req_comparison = False
    _scale = scale[0]
    questions.append(make_instance(question,answer,derivation,answer_type,answer_form,facts,mapping,rel_paragraphs,req_comparison,_scale))
    return questions

def syn_table_average(table,ori_table,shift_index,scale,return_program = False):
    questions = []
    if len(table)<=3:
        return None
    row_index = random.sample(range(1,len(table)),2)
    column_index = random.sample(range(1,len(table[0])),2)
    row0,row1 = row_index[0],row_index[1]
    col0,col1 = column_index[0],column_index[1]
    if table[row0][col0] == None or table[row0][col1] == None:
        return None
    for i in range(len(table[0])):
        if table[row1][i] == None:
            return None
    table_name = table[0][0]
    #the second row
    row_name = table[row1][0]
    values = []
    for i in range(1,len(table[0])):
        values.append(table[row1][i])
    res = np.mean(values)
    res = round(res,6)
    if int(res)==res:
        res = int(res)
    else:
        res = round(res,2)
    answer = res
    answer_type = "arithmetic"
    answer_form = "table"
    facts = []
    mapping = {"table":[],"table_col_name":[],"table_row_name":[]}
    derivation = "("
    for i in range(1,len(table[0])):
        facts.append(ori_table[row1][i])
        mapping["table"].append([row1+shift_index,i])
        mapping["table_row_name"].append(table[row1][0])
        mapping["table_col_name"].append(table[0][i])
        derivation+=ori_table[row1][i]+"+"
    derivation = derivation[:-1]
    derivation += ")/"+str(len(table[0])-1)
    rel_paragraphs =  []
    req_comparison = False
    _scale = scale[0]
    question=""
    if return_program:
        period = []
        for i in range(1,len(table[0])):
            period.append(table[0][i])
        period = " ".join(period)
        if "20" not in period:
            period = "none"
        program = "table_average ( "+row_name+", "+period+" ) "
        sub_table_name = table_name
        questions.append(make_instance(question,answer,derivation,answer_type,answer_form,facts,mapping,rel_paragraphs,req_comparison,_scale,sub_table_name,program))
    else:
        questions.append(make_instance(question,answer,derivation,answer_type,answer_form,facts,mapping,rel_paragraphs,req_comparison,_scale))
    return questions

def syn_table_division(table,ori_table,shift_index,scale,return_program = False):
    questions = []
    if len(table)<=3:
        return None
    row_index = random.sample(range(1,len(table)),2)
    column_index = random.choice(range(1,len(table[0])))
    col = column_index
    row0,row1 = min(row_index[0],row_index[1]),max(row_index[0],row_index[1])
    if table[row0][col] == None or table[row0][col] == 0 or table[row1][col] == None or table[row1][col] == 0:
        return None
    table_name = table[0][0]
    row_name1 = table[row0][0]
    row_name2 = table[row1][0]
    column_name = table[0][col]
    res = table[row0][col] / table[row1][col]*100.0
    res = round(res,6)
    if int(res)==res:
        res = int(res)
    else:
        res = round(res,2)
    answer = res
    derivation = ori_table[row0][col]+"/"+ori_table[row1][col]
    answer_type = "arithmetic"
    answer_form = "table"
    facts = []
    facts.append(ori_table[row0][col])
    facts.append(ori_table[row1][col])
    mapping = {"table":[],"table_col_name":[],"table_row_name":[]}

    mapping["table"].append([row0+shift_index,col])
    mapping["table_row_name"].append(table[row0][0])
    mapping["table_col_name"].append(table[0][col])
    mapping["table"].append([row1+shift_index,col])
    mapping["table_row_name"].append(table[row1][0])
    mapping["table_col_name"].append(table[0][col])

    rel_paragraphs =  []
    req_comparison = False
    _scale = "percent"
    question=""
    if return_program:
        item1 = "the "+row_name1+" of "+column_name
        item2 = "the "+row_name2+" of "+column_name
        program = "divide ( "+item1+", "+item2+" ) "
        sub_table_name = table_name
        questions.append(make_instance(question,answer,derivation,answer_type,answer_form,facts,mapping,rel_paragraphs,req_comparison,_scale,sub_table_name,program))
    else:
        questions.append(make_instance(question,answer,derivation,answer_type,answer_form,facts,mapping,rel_paragraphs,req_comparison,_scale))
    return questions
    
def syn_table_diff(table,ori_table,shift_index,scale,return_program = False):
    questions = []
    if len(table)<=3:
        return None
    row_index = random.choice(range(1,len(table)))
    column_index = random.sample(range(1,len(table[0])),2)
    row = row_index
    col0,col1 = min(column_index[0],column_index[1]),max(column_index[0],column_index[1])
    if table[row][col0] == None or table[row][col1] == None:
        return None
    table_name = table[0][0]
    row_name = table[row][0]
    column_name1 = table[0][col0]
    column_name2 = table[0][col1]
    res = table[row][col0] - table[row][col1]
    res = round(res,6)
    if int(res)==res:
        res = int(res)
    else:
        res = round(res,2)
    answer = res
    derivation = ori_table[row][col0]+"-"+ori_table[row][col1]
    answer_type = "arithmetic"
    answer_form = "table"
    facts = []
    facts.append(ori_table[row][col0])
    facts.append(ori_table[row][col1])
    mapping = {"table":[],"table_col_name":[],"table_row_name":[]}
    mapping["table"].append([row+shift_index,col0])
    mapping["table_row_name"].append(table[row][0])
    mapping["table_col_name"].append(table[0][col0])
    mapping["table"].append([row+shift_index,col1])
    mapping["table_row_name"].append(table[row][0])
    mapping["table_col_name"].append(table[0][col1])
    rel_paragraphs =  []
    req_comparison = False
    _scale = scale[0]
    question=""
    if return_program:
        item1 = "the "+row_name+" of "+column_name1
        item2 = "the "+row_name+" of "+column_name2
        program = "subtract ( "+item1+", "+item2+" ) "
        sub_table_name = table_name
        questions.append(make_instance(question,answer,derivation,answer_type,answer_form,facts,mapping,rel_paragraphs,req_comparison,_scale,sub_table_name,program))
    else:
        questions.append(make_instance(question,answer,derivation,answer_type,answer_form,facts,mapping,rel_paragraphs,req_comparison,_scale))
    return questions
    
def syn_table_change_ratio(table,ori_table,shift_index,scale,return_program = False):
    questions = []
    if len(table)<=3:
        return None
    if "2019" not in table[0][1:] and "2018" not in table[0][1:] and "2017" not in table[0][1:] :
        return None
    cnt = 0
    while True:
        cnt+=1
        if cnt>10:
            return None
        row_index = random.sample(range(1,len(table)),2)
        column_index = random.sample(range(1,len(table[0])),2)
        values = []
        for row in row_index:
            for column in column_index:
                values.append(table[row][column])
        valid_flag = True
        for value in values:
            if value == None or value==0:
                valid_flag=False
        if valid_flag:
            break

    col0,col1 = min(column_index[0],column_index[1]),max(column_index[0],column_index[1])
    table_name = table[0][0]
    column_name1 = table[0][col0]
    column_name2 = table[0][col1]

    for row in row_index:
        row_name = table[row][0]
        res = (table[row][col0] - table[row][col1])/table[row][col1]*100.0
        res = round(res,6)
        if int(res)==res:
            res = int(res)
        else:
            res = round(res,2)
        answer = res
        derivation = "("+ori_table[row][col0]+"-"+ori_table[row][col1]+")"+"/"+ori_table[row][col1]
        answer_type = "arithmetic"
        answer_form = "table"
        facts = []
        facts.append(ori_table[row][col0])
        facts.append(ori_table[row][col1])
        mapping = {"table":[],"table_col_name":[],"table_row_name":[]}
        mapping["table"].append([row+shift_index,col0])
        mapping["table_row_name"].append(table[row][0])
        mapping["table_col_name"].append(table[0][col0])
        mapping["table"].append([row+shift_index,col1])
        mapping["table_row_name"].append(table[row][0])
        mapping["table_col_name"].append(table[0][col1])
        rel_paragraphs =  []
        req_comparison = False
        _scale = "percent"
        question=""
        if return_program:
            item1 = "the "+row_name+" of "+column_name1
            item2 = "the "+row_name+" of "+column_name2
            program = "subtract ( "+item1+", "+item2+" ) , divide ( #0, "+item2+" ) "
            sub_table_name = table_name
            questions.append(make_instance(question,answer,derivation,answer_type,answer_form,facts,mapping,rel_paragraphs,req_comparison,_scale,sub_table_name,program))
        else:
            questions.append(make_instance(question,answer,derivation,answer_type,answer_form,facts,mapping,rel_paragraphs,req_comparison,_scale))
    return questions