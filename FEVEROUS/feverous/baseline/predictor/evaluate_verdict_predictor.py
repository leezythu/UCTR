import pandas as pd
import sys
from datetime import datetime
import pickle
import math
from collections import Counter
from transformers import BertForSequenceClassification, Trainer, TrainingArguments, AdamW, BertTokenizer, BertPreTrainedModel, BertModel,  RobertaForSequenceClassification, RobertaTokenizer
from transformers.modeling_outputs import SequenceClassifierOutput
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
from sklearn.model_selection import train_test_split
import torch
from sklearn.model_selection import KFold
import numpy as np
import collections
import argparse
import jsonlines
import itertools
import random
import copy
from tqdm import tqdm
import os
from utils.log_helper import LogHelper

from utils.annotation_processor import AnnotationProcessor, EvidenceType
from utils.prepare_model_input import prepare_input, init_db

LogHelper.setup()
logger = LogHelper.get_logger(__name__)

class FEVEROUSDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels, use_labels = True):
        self.encodings = encodings
        self.labels = labels
        self.use_labels = use_labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        if self.use_labels:
            item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

def process_data(claim_verdict_list):

    map_verdict_to_index = {'NOT ENOUGH INFO': 0, 'SUPPORTS': 1, 'REFUTES': 2}
    text = [x[0] for x in claim_verdict_list]#["I love Pixar.", "I don't care for Pixar."]

    labels = [map_verdict_to_index[x[1]] for x in claim_verdict_list] #get value from enum
    # map_verdict_to_index = {'SUPPORTS': 0, 'REFUTES': 1}
    # text = []
    # labels = []
    # for x in claim_verdict_list:
    #     if x[1] in map_verdict_to_index:
    #         text.append(x[0])
    #         labels.append(map_verdict_to_index[x[1]])
    return text, labels



def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='micro')
    acc = accuracy_score(labels, preds)
    class_rep = classification_report(labels, preds, labels= [0,1,2],target_names= ['NOT ENOUGH INFO', 'SUPPORTS', 'REFUTES'], output_dict=True)
    logger.info(class_rep)
    logger.info("Acc: {}, Recall: {}, Precision: {}, F1: {}".format(acc, recall, precision, f1))
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall,
        'class_rep': class_rep
    }



def model_trainer(args, test_dataset):
    print("model_path",args.model_path)
    # model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels =4)
    if args.model_path == "models/raw_roberta_large":
        print("using raw roberta with random classifier...")
        model = RobertaForSequenceClassification.from_pretrained(args.model_path, num_labels =3, return_dict=True)
    else:
        model = RobertaForSequenceClassification.from_pretrained(args.model_path,return_dict=True)


    #anfs/bigdisc/rmya2/faiss_data/model_verdict_predictor/checkpoint-1500'
    training_args = TrainingArguments(
    output_dir='./results',          # output directory
    per_device_eval_batch_size=32,   # batch size for evaluation
    )

    trainer = Trainer(
    model=model,                         # the instantiated 🤗 Transformers model to be trained
    args=training_args,                  # training arguments, defined above
    eval_dataset=test_dataset,          # evaluation dataset
    compute_metrics = compute_metrics,
    )
    return trainer, model

def report_average(reports):
    mean_dict = dict()
    for label in reports[0].keys():
        dictionary = dict()

        if label in 'accuracy':
            mean_dict[label] = sum(d[label] for d in reports) / len(reports)
            continue

        for key in reports[0][label].keys():
            dictionary[key] = sum(d[label][key] for d in reports) / len(reports)
        mean_dict[label] = dictionary
    return mean_dict


def claim_evidence_predictor(annotations_dev, args):
    # if not os.path.exists("claim_evidence_input_test_for_evaluate"):
    claim_evidence_input_test = [(prepare_input(anno, 'schlichtkrull'), anno.get_verdict()) for anno in tqdm(annotations_dev)]
    claim_evidence_input_test_for_evaluate = open("claim_evidence_input_test_for_evaluate",'wb')
    pickle.dump(claim_evidence_input_test,claim_evidence_input_test_for_evaluate)

    print("loading pickles...")
    claim_evidence_input_test_for_evaluate = open("claim_evidence_input_test_for_evaluate",'rb')
    claim_evidence_input_test = pickle.load(claim_evidence_input_test_for_evaluate)

    logger.info("Sample instance {}".format(claim_evidence_input_test[0][0]))
    text_test, labels_test = process_data(claim_evidence_input_test)
        
    tokenizer = RobertaTokenizer.from_pretrained('roberta-large')

    # tokenizer = RobertaTokenizer.from_pretrained('ynie/roberta-large-snli_mnli_fever_anli_R1_R2_R3-nli')
    text_test = tokenizer(text_test, padding=True, truncation=True)
    test_dataset = FEVEROUSDataset(text_test, labels_test)

    trainer, model = model_trainer(args, test_dataset)
    predictions = trainer.predict(test_dataset)
    predictions = predictions.predictions.argmax(-1)
    print("len")
    print(len(annotations_dev))
    print(len(predictions))
    i=0
    predictions_map = {}
    # for annota,claim_evidence in zip(annotations_dev,claim_evidence_input_test):
    #     if claim_evidence[1] in ['SUPPORTS','REFUTES']:
    #         predictions_map[annota.get_id()] = predictions[i]
    #         i+=1
    predictions_map = {annota.get_id():predictions[i] for i,annota in enumerate(annotations_dev)}

    map_verdict_to_index = {0:'NOT ENOUGH INFO', 1:'SUPPORTS', 2:'REFUTES'}
    # map_verdict_to_index = {0:'SUPPORTS', 1:'REFUTES'}

    with jsonlines.open(os.path.join(args.input_path.split('.jsonl')[0] + '.verdict.jsonl'), 'w') as writer:
        with jsonlines.open(os.path.join(args.input_path)) as f:
             for i,line in enumerate(f.iter()):
                 if i == 0:
                     writer.write({'header':''}) # skip header line
                     continue
                 # if len(line['evidence'][0]['content']) == 0: continue
                 line['predicted_label'] = map_verdict_to_index[predictions_map[line['id']]]
                #  if line["id"] in predictions_map:
                #     line['predicted_label'] = map_verdict_to_index[predictions_map[line['id']]]
                #  else:
                #     line['predicted_label'] = 'SUPPORTS'
                 writer.write(line)

    logger.info('Finished predicting verdicts...')

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str, help='/path/to/data')
    parser.add_argument('--model_path', type=str, help='/path/to/data')
    parser.add_argument('--wiki_path', type=str)

    args = parser.parse_args()

    annotations_dev = None
    anno_processor_dev = AnnotationProcessor(args.input_path)#, has_content = True)
    init_db(args.wiki_path)
    annotations_dev = [annotation for annotation in anno_processor_dev]

    logger.info('Start predicting verdicts...')
    claim_evidence_predictor(annotations_dev, args)



if __name__ == "__main__":
    main()
