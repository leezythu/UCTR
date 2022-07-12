#### Program Collecting

Download the template file 

[all_data.json]: https://github.com/czyssrs/Logic2Text

 , and then run:

```python
python process_program.py
```

#### Data Generation

```python
python syn.py
```

For NL-Generator, we use a gpt-2 model from . After downloading the required model, please run:

```

```

#### Model Training&Inference

We use the baseline model from , so we first clone the training scripts from . For training and inference, please run:

```python
sh train_verdict.sh
sh infer_verdict.sh
```

