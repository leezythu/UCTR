python run_summarization.py \
    --model_name_or_path t5-small \
    --do_train \
    --do_eval \
    --do_predict \
    --train_file sql2text_train.json \
    --validation_file sql2text_valid.json \
    --test_file sql2text_valid.json \
    --source_prefix "summarize: " \
    --output_dir result \
    --overwrite_output_dir \
    --per_device_train_batch_size=8 \
    --per_device_eval_batch_size=8 \
    --predict_with_generate \
    --num_train_epochs 10 \
    --evaluation_strategy epoch