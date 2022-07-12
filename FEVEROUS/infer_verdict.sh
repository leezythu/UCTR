# model="feverous_verdict_predictor_from_train_cell_only_label_3_0620"
# model="feverous_verdict_predictor_from_data_50_0706"
model="feverous_verdict_predictor_from_syn+count_label_3_no_nei_0617_by_step"
#on retrieved
# CUDA_VISIBLE_DEVICES=4 PYTHONPATH=src/feverous python src/feverous/baseline/predictor/evaluate_verdict_predictor.py --input_path data/test.combined.not_precomputed.p5.s5.t3.cells.jsonl --wiki_path data/feverous_wikiv1.db --model_path models/${model}/checkpoint-300

# on golden
CUDA_VISIBLE_DEVICES=4 PYTHONPATH=src/feverous python src/feverous/baseline/predictor/evaluate_verdict_predictor.py --input_path data/dev_eval.jsonl --wiki_path data/feverous_wikiv1.db --model_path models/${model}/checkpoint-7200
# CUDA_VISIBLE_DEVICES=4 PYTHONPATH=src/feverous python src/feverous/baseline/predictor/evaluate_verdict_predictor.py --input_path data/dev_eval.jsonl --wiki_path data/feverous_wikiv1.db --model_path models/feverous_verdict_predictor
