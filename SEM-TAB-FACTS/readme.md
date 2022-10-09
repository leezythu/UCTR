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

#### Model Training&Inference

```python
git clone git@github.com:devanshg27/sem-tab-fact.git
mv train_a.sh sem-tab-fact/
mv infer_a.sh sem-tab-fact/
sh train_a.sh
sh infer_a.sh
```

