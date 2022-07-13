import json
from my_utils import *
import copy
from qa_gen import *

def syn_table_qa(table,ori_table,shift_index,scale,type,return_program = False):
    if type == "span":
        return syn_table_span(table,ori_table,shift_index,scale,return_program)
    elif type == "multi-span":
        return syn_table_multi_span(table,ori_table,shift_index,scale,return_program )
    elif type == "average":
        return syn_table_average(table,ori_table,shift_index,scale,return_program )
    elif type == "diff":
        return syn_table_diff(table,ori_table,shift_index,scale,return_program )
    elif type == "change_ratio":
        return syn_table_change_ratio(table,ori_table,shift_index,scale,return_program )
    else:
        pass

def syn_text_qa(text,rel_index):
    syn_questions = []
    res = nlp.qg_without_answer(text)
    for qa_pair in res:
        question = qa_pair["question"]
        answer = []
        answer.append(qa_pair["answer"])
        derivation = ""
        answer_type = "span"
        answer_form = "text"
        facts = answer
        mapping = {"paragraph":{}}
        mapping["paragraph"][str(rel_index)] = []
        # print(text)
        # print(qa_pair["answer"])
        try:
            start_idx = text.index(qa_pair["answer"])
        except:
            continue
        end_idx = start_idx + len(qa_pair["answer"])
        mapping["paragraph"][str(rel_index)].append(
            [start_idx,end_idx]
        )
        rel_paragraphs =  []
        rel_paragraphs.append(str(rel_index))
        req_comparison = False
        _scale = ""
        syn_questions.append(make_instance(question,answer,derivation,answer_type,answer_form,facts,mapping,rel_paragraphs,req_comparison,_scale))
    return syn_questions

def table_relate(table,paras,return_program = False):
    syn_q = []
    scale = get_scale(table,paras)
    if len(scale)>1:
        fail_cnt[0]+=1
        return None
    if scale[0]=="":
        fail_cnt[1]+=1
        return None
    drop_unuseful_info(table)
    ori_header_index = aggregate_header(table)
    if ori_header_index==None:#没有找到正确的header
        fail_cnt[2]+=1
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
        # if table[0][0]=="":
        #     table[0][0] = "Items"
        ori_table = copy.deepcopy(sub_table)
        max_number = normalize_table(sub_table)
        if scale[0]=="percent" and max_number>100:
            print("not pure percent scale...")
            continue
        print("scale:",scale)
        # res = syn_table_qa(sub_table,ori_table,shift_index,scale,type="span")
        # if res != None:
        #     syn_q.extend(res)
        # res = syn_table_qa(sub_table,ori_table,shift_index,scale,type="average")
        # if res != None:
        #     syn_q.extend(res)
        res = syn_table_qa(sub_table,ori_table,shift_index,scale,type="diff",return_program=return_program)
        if res != None:
            syn_q.extend(res)
        res = syn_table_qa(sub_table,ori_table,shift_index,scale,type="change_ratio",return_program=return_program)
        if res != None:
            syn_q.extend(res)
    return syn_q


if __name__=="__main__":
    # nlp = pipeline("question-generation", model='valhalla/t5-base-qg-hl', qg_format="highlight")
    input_path = "dataset_tagop/tatqa_dataset_all.json"
    out_path = "./syn_for_arithmetic.jsonl"
    input_f = open(input_path)
    out_f =  open(out_path,'w')
    samples = json.load(input_f)
    succ_cnt = 0
    fail_cnt = [0,0,0,0]
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

        # texts = [para["text"] for para in paras]
        # target_text = ""
        # for i in range(len(texts)):
        #     if len(texts[i]) > len(target_text):
        #         target_text = texts[i]
        #         rel_index = i+1
        # syn_q = syn_text_qa(target_text,rel_index)
        # syn_questions.extend(syn_q)

        if len(syn_questions) == 0:
            fail_cnt[3]+=1
            continue
        sample["questions"] = syn_questions
        succ_cnt += 1 
        out_f.write(json.dumps(sample)+"\n")
        # exit(0)
    print("succ cnt:",succ_cnt)
    print("fail cnt:",fail_cnt)
    # #转换格式到可以训练的状态