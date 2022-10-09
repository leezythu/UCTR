import json
from my_utils import *
import copy

def syn_table_qa(table,ori_table,shift_index,scale,type,return_program = False):
    if type == "span":
        return syn_table_span(table,ori_table,shift_index,scale,return_program)
    elif type == "multi-span":
        return syn_table_multi_span(table,ori_table,shift_index,scale,return_program )
    elif type == "average":
        return syn_table_average(table,ori_table,shift_index,scale,return_program )
    elif type == "division":
        return syn_table_division(table,ori_table,shift_index,scale,return_program )
    elif type == "diff":
        return syn_table_diff(table,ori_table,shift_index,scale,return_program )
    elif type == "change_ratio":
        return syn_table_change_ratio(table,ori_table,shift_index,scale,return_program )
    else:
        pass

def table_relate(table,paras,return_program = False):
    syn_q = []
    scale = get_scale(table,paras)
    if len(scale)>1:
        return None
    if scale[0]=="":
        return None
    drop_unuseful_info(table)
    ori_header_index = aggregate_header(table)
    if ori_header_index==None:
        return None
    header_index = 0
    midheader_index = find_midheader_index(table)
    print("ori_header_index:",ori_header_index)
    print("midheader_index",midheader_index)
    sub_tables,meta_info = split_table(table,header_index,midheader_index)
    if len(midheader_index)==0:
        midheader_index = [0]
    for mid_index,sub_table in zip(midheader_index,sub_tables):
        #for table
        shift_index = ori_header_index+mid_index
        ori_table = copy.deepcopy(sub_table)
        max_number = normalize_table(sub_table)
        if scale[0]=="percent" and max_number>100:
            print("not pure percent scale...")
            continue
        print("scale:",scale)
        # Each question in TAT-QA corresponds to a specific type. For the `span` and `multi-span` types, we just select values in a table and linearize them into a sentence. 
        # For the other types, we synthetic programs, which are to be converted to natural languages.
        # res = syn_table_qa(sub_table,ori_table,shift_index,scale,type="span")
        # if res != None:
        #     syn_q.extend(res)
        # res = syn_table_qa(sub_table,ori_table,shift_index,scale,type="multi-span")
        # if res != None:
        #     syn_q.extend(res)
        #In experiments, `sum`, `count` and `multiplication` didn't bring improvement, so we omit these types here.
        res = syn_table_qa(sub_table,ori_table,shift_index,scale,type="average",return_program=return_program)
        if res != None:
            syn_q.extend(res)
        res = syn_table_qa(sub_table,ori_table,shift_index,scale,type="division",return_program=return_program)
        if res != None:
            syn_q.extend(res)
        res = syn_table_qa(sub_table,ori_table,shift_index,scale,type="diff",return_program=return_program)
        if res != None:
            syn_q.extend(res)
        res = syn_table_qa(sub_table,ori_table,shift_index,scale,type="change_ratio",return_program=return_program)
        if res != None:
            syn_q.extend(res)
    return syn_q

if __name__=="__main__":
    input_path = "dataset_tagop/tatqa_dataset_all.json"
    out_path = "./syn_for_arithmetic_table_only.jsonl"
    input_f = open(input_path)
    out_f =  open(out_path,'w')
    samples = json.load(input_f)
    succ_cnt = 0
    return_program = True
    for i in range(len(samples)):
        print(i)
        syn_questions = []
        sample = samples[i]
        paras = sample["paragraphs"]
        table = copy.deepcopy(sample["table"]["table"])

        syn_q = table_relate(table,paras,return_program)
        if syn_q != None:
            syn_questions.extend(syn_q)

        if len(syn_questions) == 0:
            continue
        sample["questions"] = syn_questions
        succ_cnt += 1 
        out_f.write(json.dumps(sample)+"\n")
    print("succ cnt:",succ_cnt)