## Data
We have put the generated data into the file `tatqa/dataset_tagop/tatqa_dataset_synthetic_data.json`. You can directly use it for the model training and inference. If you want to generate it yourself, please follow the following steps:

### Program Collecting

In the finqa folder
- we collect arithmetic expressions from [FinQA](https://github.com/czyssrs/FinQA) and split them into train_op2nl/dev_op2nl.json using `collect_data.py`.
- Based on the above files, we train a Bart model to convert arithmetic expressions to natural language questions. You can download our trained model from [google drive](https://drive.google.com/file/d/1qkYb1v1snmjLL-DwlyrJGWUqpCaia1Xh/view?usp=sharing) and put it in the `op2nl_output` directory.
```
sh run.sh
```

### Data Generation (Arithmetic expression)
Note that TAT-QA contains questions for table-only, text-only, and table-text. So we have to generate questions of each type.

1. text-only
We utilize the texual question generation pipeline from [this repository](https://github.com/teacherpeterpan/Unsupervised-Multi-hop-QA).
```python
cd tatqa
python syn_for_arithmetic_text_only.py
```
2. table-only
We generate diverse programs from tables.
```python
python syn_for_arithmetic_table_only.py
```
Then you can put the generated file into finqa and convert programs to natural language sentences.
```python
cd finqa
sh infer.sh
```
3. table-text
The `table-to-text` operator converts a table into a sub-table and a generated sentence. The `text-to-table` operator integrate information in text into an expanded table.
```python
python syn_for_arithmetic_table_text.py
```
### Data Generation (SQL query)

```python
cd sql2text
```
Firstly please download the [Squall dataset](https://github.com/tzshi/squall). Then run:
```python
python collect_sql2text_from_squall.py
```
and further split the generated data into sql2text_train.json and sql2text_valid.json.
Then we can train a model to convert SQL language to natural language. You can also download our trained model from [google drive](https://drive.google.com/file/d/1CS1vdS6CnYgOto4RoKSVzjzIvlj5joj3/view?usp=sharing)
```python
sh trainer.sh
```
To synthetic programs from tables, run
```python
sh insert_train_csv.sh #insert tables to db using csvs-to-sqlite
python generate_command_from_squall.py
python tatqa-qag.py
```
```python
python sql2nl.py #step 1
sh infer.sh #generate sentences from SQLs
python sql2nl.py#step 2
```

Finally, we aggregate the all samples generated above to form the final data file `tatqa_dataset_synthetic_data.json`

## Model Training&Inference
Tagop use `RoBERTa` as its encoder and the following commands are to prepare RoBERTa model:

```bash
cd tatqa/dataset_tagop
mkdir roberta.large && cd roberta.large
wget -O pytorch_model.bin https://s3.amazonaws.com/models.huggingface.co/bert/roberta-large-pytorch_model.bin
wget -O config.json https://s3.amazonaws.com/models.huggingface.co/bert/roberta-large-config.json
wget -O vocab.json https://s3.amazonaws.com/models.huggingface.co/bert/roberta-large-vocab.json
wget -O merges.txt https://s3.amazonaws.com/models.huggingface.co/bert/roberta-large-merges.txt
```

```python
sh train.sh
```