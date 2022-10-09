import json
from my_utils import *
import copy
from text_qa_gen import *

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

if __name__=="__main__":
    # for textual question generation, we follow the implementation of the paper `Unsupervised Multi-hop Question Answering by Question Generation`
    nlp = pipeline("question-generation", model='valhalla/t5-base-qg-hl', qg_format="highlight")
    input_path = "dataset_tagop/tatqa_dataset_all.json"
    out_path = "./syn_for_arithmetic_text_only.jsonl"
    input_f = open(input_path)
    out_f =  open(out_path,'w')
    samples = json.load(input_f)
    return_program = True
    for i in range(len(samples)):
        print(i)
        syn_questions = []
        sample = samples[i]
        paras = sample["paragraphs"]
        texts = [para["text"] for para in paras]
        target_text = ""
        for i in range(len(texts)):
            if len(texts[i]) > len(target_text):
                target_text = texts[i]
                rel_index = i+1
        syn_q = syn_text_qa(target_text,rel_index)
        syn_questions.extend(syn_q)

        if len(syn_questions) == 0:
            continue
        sample["questions"] = syn_questions
        out_f.write(json.dumps(sample)+"\n")