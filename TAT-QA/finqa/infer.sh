python prepare_infer_data.py --input_file syn_for_arithmetic_table_only.jsonl --output_file syn_for_arithmetic_table_only_op.json

python predict_translation.py \
    --model_name_or_path  op2nl_output/ \
    --output_dir  infer_res_arithmetic_table_only\
    --test_file ./syn_for_arithmetic_table_only_op.json \
    --source_lang program \
    --target_lang nl \
    --per_device_test_batch_size 32 

python prepare_infer_data_2.py --op_file ./syn_for_arithmetic_table_only.jsonl --op2nl_file infer_res_arithmetic_table_only/res.jsonl --output_file tatqa_dataset_arithmetic2text_table_only.json