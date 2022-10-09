import argparse
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)
    args = parser.parse_args()
    input_file = args.input_file
    output_file = args.output_file
    with open(input_file, "r") as f:
        with open(output_file, "w") as fw:
            for line in f:
                line = line.strip()
                line = json.loads(line)
                for q in line["questions"]:
                    program = q["program"]
                    sub_table_name = q["sub_table_name"]
                    sample = {"translation":{}}
                    # sample["translation"]["program"] = line["qa"]["question"]
                    sample["translation"]["golden"] = q["question"]
                    sample["translation"]["program"] = program
                    sample["translation"]["nl"] = ""
                    sample["translation"]["sub_table_name"] = sub_table_name
                    fw.write(json.dumps(sample)+"\n")
