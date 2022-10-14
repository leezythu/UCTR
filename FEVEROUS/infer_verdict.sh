model="feverous_verdict_predictor_from_data_0706"
# on golden
CUDA_VISIBLE_DEVICES=4 PYTHONPATH=src/feverous python src/feverous/baseline/predictor/evaluate_verdict_predictor.py --input_path data/dev_eval.jsonl --wiki_path data/feverous_wikiv1.db --model_path models/${model}/checkpoint-7200
