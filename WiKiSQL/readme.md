### Data Generation 

```python
cd sql2text
```
Firstly please download the [Squall dataset](https://github.com/tzshi/squall). Then run:
```python
python collect_sql2text_from_squall.py
```
and further split the generated data into sql2text_train.json and sql2text_valid.json.
Then we can train a model to convert SQL language to natural language.
```python
sh trainer.sh
```

Then we collect templates from Squall (you can directly use the output file `filtered_commands.jsonl`):
```python
python generate_command_from_squall.py 
```

To synthetic programs from tables, run
```python
python syn.py
sh infer_syn.sh
```

Finally, we aggregate the all samples generated above to form the final data file `train.jsonl`, and put in into the `Table-Pretraining/examples/raw_dataset/wikisql_syn/data` directory.

## Model Training&Inference

```python
cd Table-Pretraining/examples
sh process.sh #process data
sh train_syn.sh
'''