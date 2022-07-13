mode="train"
day="0705"
gpu_index=1
# Prepare dataset: 
# PYTHONPATH=$PYTHONPATH:$(pwd):$(pwd)/tag_op python tag_op/prepare_dataset.py --mode ${mode}

CUDA_VISIBLE_DEVICES=${gpu_index} PYTHONPATH=$PYTHONPATH:$(pwd) python tag_op/trainer.py --train_source ${mode} --data_dir tag_op/cache/ \
--save_dir ./tmp --batch_size 16 --eval_batch_size 8 --max_epoch 100 --warmup 0.06 --optimizer adam --learning_rate 3e-4 \
--weight_decay 5e-5 --seed 123 --gradient_accumulation_steps 4 --bert_learning_rate 1e-5 --bert_weight_decay 0.01 \
--log_per_updates 50 --eps 1e-6 --encoder roberta \
# --model_path  checkpoint_0612_syn_text_sql2text_arithmetic2text_t2p_with_double_diff_and_changeratio