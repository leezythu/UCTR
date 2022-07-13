import json

def fill_in_column(sql,columns,tbl):
    column_dict = {}
    for i in range(len(columns)):
        column_dict["c"+str(i+1)] = columns[i][0]
    # print(column_dict)
    sql = sql.split()
    for i in range(len(sql)):
        if sql[i].split("_")[0] in column_dict:
            sql[i] = "["+column_dict[sql[i].split("_")[0]]+"]"
        # elif sql[i] == 'w':
        #     sql[i] = "["+tbl+"]"
        else:
            sql[i] = sql[i]
    sql = " ".join(sql)
    return sql

def collect(samples,out_f):
    succ_cnt = 0
    for i in range(len(samples)):
        tbl = samples[i]['tbl']
        sql = samples[i]['sql']
        nl = samples[i]['nl']
        nl = " ".join(nl)
        sql = " ".join(item[1] for item in sql)
        columns = samples[i]['columns']
        sql = fill_in_column(sql,columns,tbl)
        # print(sql,nl)
        if "id" in sql:
            continue
        if "[]" in sql or "!=" in sql:
            continue
        if " - " in sql:
            continue
        elif " + " in sql:
            continue
        elif "count" in sql or "sum" in sql:
            continue
        elif ">" in sql or "<" in sql:
            continue
        # elif "min" in pair["template"] or "max" in pair["template"] or "order" in pair["template"] :
        #     pair["type"] = "compare"
        # elif multi_ans(pair["res"]):
        #     pair["type"] = "spans"
        # else:
        #     pair["type"] = "word matching"
        succ_cnt+=1
        out_f.write(json.dumps({"text":sql,"summary":nl})+"\n")

if __name__ == "__main__":
    input = json.load(open("squall.json"))
    out_f = open("sql2text_all.json",'w')
    collect(input,out_f)
    out_f.close()