import argparse
import json
from os import replace
import random

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--op_file", type=str, required=True)
    parser.add_argument("--op2nl_file", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)
    args = parser.parse_args()
    op_file = args.op_file
    op2nl_file = args.op2nl_file
    output_file = args.output_file
    samples = []
    k = 0
    with open(op_file, "r") as op:
        with open(op2nl_file, "r") as op2nl:
            for op_line in op:
                # k+=1
                # if k>1000:
                #     break
                op_line = json.loads(op_line)
                for q in op_line["questions"]:
                    replacement =  json.loads(op2nl.readline())["pred"]
                    if "total" not in replacement:
                        q["question"] = replacement
                        if q["sub_table_name"]!="":
                            q["question"]+=" for "+q["sub_table_name"]
                    else:
                        print(replacement)
                # pred = json.loads(op2nl.readline())["pred"]
                # if op_line["qa"]["answer"] == "n/a":
                #     continue
                # op_line["qa"]["question"] = pred
                samples.append(op_line)
    random.shuffle(samples)
    with open(output_file, "w") as fw:
        fw.write(json.dumps(samples))

