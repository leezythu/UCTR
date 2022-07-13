#### Program Collecting

We collect arithmetic expressions from [finqa](https://github.com/czyssrs/FinQA).

#### Data Generation (Arithmetic expression)

```python
python syn_for_arithmetic.py
cd generator
sh infer.sh
```

#### Data Generation (SQL query)

```python
cd sql2text
sh infer.sh
python sql2nl.py
```

#### Model Training&Inference

```python
sh train.sh
```

