# python prepare_infer_data.py --input_file syn_samples.jsonl --output_file syn_samples_op.json
# python prepare_infer_data.py --input_file syn_for_arithmetic.jsonl --output_file syn_for_arithmetic_op.json


# python predict_translation.py \
#     --model_name_or_path  op2nl_output/epoch_10 \
#     --output_dir  infer_res\
#     --test_file ./syn_for_arithmetic_op.json \
#     --source_lang program \
#     --target_lang nl \
#     --per_device_test_batch_size 32 

python prepare_infer_data_2.py --op_file ./syn_for_arithmetic.jsonl --op2nl_file infer_res/res.jsonl --output_file ../dataset/tatqa_dataset_arithmetic2text_only_diff_changeratio.json