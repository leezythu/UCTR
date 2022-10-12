#### Program Collecting

Download the template file [all_data.json](https://github.com/czyssrs/Logic2Text) , and then run

```python
python process_program.py
```

#### Data Generation

```python
git clone https://github.com/Raldir/FEVEROUS.git
python syn.py
```

For NL-Generator, we use a GPT-2 model from [here](https://github.com/czyssrs/Logic2Text). Please download the model and scripts, and put them into a directory named gpt_base. Then run:

```python
cd gpt_base
python preprocess.py data_folder GPT_folder
```

After fine-tuning the model, you can generate synthetic claims from collected programs:

```python
sh generate.sh
```

#### Model Training&Inference

We use the baseline model from the official repository of [FEVEROUS](https://github.com/Raldir/FEVEROUS), so you can first clone the training scripts. Then download the FEVEROUS data using `./scripts/download_data.sh` and replace the training file with the synthetic file.

For training and inference, please run:
```python
sh train_verdict.sh
sh infer_verdict.sh
```

