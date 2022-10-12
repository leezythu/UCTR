source="data"
day="0706"

# syn_wo_t2t
# CUDA_VISIBLE_DEVICES=0 PYTHONPATH=src/feverous python src/feverous/baseline/predictor/train_verdict_predictor.py --wiki_path data/feverous_wikiv1.db --model_path models/feverous_verdict_predictor_from_${source}_label_3_${day} --input_path ${source}  --pretrained_path roberta-large --num_label 3  > ${source}_label_3_${day}.log

# mqaqg
# CUDA_VISIBLE_DEVICES=2 PYTHONPATH=src/feverous python src/feverous/baseline/predictor/train_verdict_predictor.py --wiki_path data/feverous_wikiv1.db --model_path models/feverous_verdict_predictor_from_mqaqg_label_3_0606 --input_path syn_wo_t2t_sen  --pretrained_path roberta-large --sample_nei --num_label 3

#raw
# CUDA_VISIBLE_DEVICES=4 PYTHONPATH=src/feverous python src/feverous/baseline/predictor/train_verdict_predictor.py --wiki_path data/feverous_wikiv1.db --model_path models/feverous_verdict_predictor_from_raw_label_3 --input_path data --num_label 3 --pretrained_path roberta-large --sample_nei 

# syn
CUDA_VISIBLE_DEVICES=0 PYTHONPATH=src/feverous python src/feverous/baseline/predictor/train_verdict_predictor.py --wiki_path data/feverous_wikiv1.db --model_path models/feverous_verdict_predictor_from_${source}_${day} --input_path ${source}  --num_label 3 --pretrained_path roberta-large > ${source}_${day}.log

#aug
# CUDA_VISIBLE_DEVICES=0 PYTHONPATH=src/feverous python src/feverous/baseline/predictor/train_verdict_predictor.py --wiki_path data/feverous_wikiv1.db --model_path models/feverous_verdict_predictor_from_${source}_${day}_aug --input_path ${source} --num_label 3   --pretrained_path models/feverous_verdict_predictor_from_syn+count_label_3_no_nei_0617_by_step/checkpoint-7200 > ${source}_label_3_${day}_aug.log