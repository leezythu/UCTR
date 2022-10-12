#### Program Collecting

We used the same templates as in FEVEROUS.

Download the template file [all_data.json](https://github.com/czyssrs/Logic2Text) , and then run

```python
python process_program.py
```

#### Data Generation

```python 
python syn.py			
```

For NL-Generator, the training and inference procedures are the same as in FEVEROUS. Then we add a filtration step:

```python
python syn_filter.py
```

Then put the generated data into the `tsv` folder as `train_3way_set.tsv`.

#### Model Training&Inference

```python
git clone git@github.com:devanshg27/sem-tab-fact.git
cp train_a.sh sem-tab-fact/
cp infer_a.sh sem-tab-fact/
cp -r csv sem-tab-fact/
cp -r tsv sem-tab-fact/
cd sem-tab-fact
sh train_a.sh #you may need to set the data path and model saving path in train_task_a/tapas_stf.py
sh infer_a.sh
```

