python prepare_input.py

python run_summarization.py \
    --model_name_or_path model \
    --do_predict \
    --train_file sql2nl_wikisql.json \
    --validation_file sql2nl_wikisql.json \
    --test_file sql2nl_wikisql.json \
    --source_prefix "summarize: " \
    --output_dir result_wikisql \
    --overwrite_output_dir \
    --per_device_train_batch_size=32 \
    --per_device_eval_batch_size=32 \
    --predict_with_generate

python post_process.py