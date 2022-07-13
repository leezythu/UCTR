#### Program Collecting

We used the same templates as in FEVEROUS.

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
sh train_a.sh
sh infer_a.sh
```

