import json,csv
input_folder = "syn"
src_f = open("gpt_base/"+input_folder+"/results/wiki_tems/wiki_tems_text.res.txt")
src = json.load(src_f)
name = "syn"
out_f = open("syn_data/"+name+".tsv",'w')
header = ('id', 'annotator', 'position', 'question', 'table_file',
			'answer_coordinates', 'answer_text', 'aggregation', 'float_answer')
tsv_writer = csv.DictWriter(out_f, delimiter='\t', fieldnames=header)
tsv_writer.writeheader()

print("total:",len(src))
ind = -1
old_table = "none"
for i in range(len(src)):
    if i%1000==0:
        print(i)
    must_have = src[i]["must_have"]
    generated = src[i]["generated"]
    type = src[i]["type"]
    if type == "count":
        continue
    if "none" in generated:
        continue
    flag = True
    for have in must_have:
        if str(have).lower() not in generated.lower():
            flag = False
    if flag:
        if src[i]["label"]:
            answer = 1
        else:
            answer = 0
        if old_table != src[i]["table_file"]:
            ind+=1
            old_table = src[i]["table_file"]
        tsv_writer.writerow({
            'id':
            ind,
			'annotator':
				'0',
			'position':
				'0',
			'question':
				src[i]["generated"],
			'table_file':
				src[i]["table_file"],
			'answer_coordinates': [],
			'answer_text':
				answer,
			'aggregation':
				None,
			'float_answer':
				None,
		})

