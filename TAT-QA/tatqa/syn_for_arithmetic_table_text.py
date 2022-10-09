import json
from my_utils import *
import copy

def linearize_row(mapping,table_name,value):
    row_name = mapping["table_row_name"][1]
    column_name = mapping["table_col_name"][1]
    # directly linearizing the row provides relatively good performance
    if table_name!="":
        gen_text = "The "+row_name+" is "+value+" when "+table_name+" is "+column_name
    else:
        gen_text = "The "+row_name+" is "+value+" when it is "+column_name
    #or we can use the describe_ent operator proposed in `Unsupervised Multi-hop Question Answering by Question Generation`. But it has to be further fed into a generative model which takes a longer time.
    # if table_name != "":
    #     t2p_flattened_table = "The "+table_name+" is "+column_name+" . "+"The "+row_name+" is "+ori_table[row][col1]+" . Start describing "+row_name+" : "
    # else:
    #     t2p_flattened_table = "The item is "+column_name+" . "+"The "+row_name+" is "+ori_table[row][col1]+" . Start describing "+row_name+" : "
    # predictor = get_GPT2_Predictor('table2text_GPT2_medium_ep9.pt', num_samples = 1)
    # gen_text = predictor.predict_output(t2p_flattened_table)
    return gen_text

def table2text(out_path):
    src_f = open("tatqa_dataset_arithmetic2text_table_only.json")
    src = json.load(src_f)
    succ_cnt = 0
    syn_samples = []
    # out_f =  open(out_path,'w')
    for sample in src:
        for i in range(len(sample["questions"])):
            data = copy.deepcopy(sample)
            question = data["questions"][i]
            table = data["table"]["table"]
            paras = data["paragraphs"]
            table_name = question["sub_table_name"]
            syn_questions = []
            mapping = question["mapping"]
            if "table" not in mapping:
                continue
            if len(mapping["table"])<2:
                continue
            #choose the second value
            t2p_col_index = mapping["table"][1][1]
            value = str(table[mapping["table"][1][0]][mapping["table"][1][1]])
            del mapping["table"][1]
            # print(t2p_col_index)
            gen_text = linearize_row(mapping,table_name,value)
            start = gen_text.index(value)
            end  = start + len(value)
            #revise mapping
            mapping["paragraph"] = {}
            mapping["paragraph"][str(len(paras)+1)] = []
            mapping["paragraph"][str(len(paras)+1)].append([start,end])
            syn_q = question
            if syn_q != None :   
                syn_questions.append(syn_q)

            if len(syn_questions) == 0:
                continue

            data["questions"] = syn_questions

            for row in table:
                del row[t2p_col_index]
            data["paragraphs"].append({"uid":None,"order":len(paras)+1,"text":gen_text})
            succ_cnt += 1 
            # out_f.write(json.dumps(data)+"\n")
            syn_samples.append(data)
    
    print("succ cnt:",succ_cnt)
    with open(out_path,'w') as f:
        f.write(json.dumps(syn_samples))


if __name__=="__main__":
    out_path = "./syn_for_arithmetic_t2p.json"
    table2text(out_path)
    #ablation
    # text2table(out_path)
 