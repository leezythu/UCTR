python run_translation_no_trainer.py \
    --model_name_or_path  ../bart-base \
    --output_dir  op2nl_output\
    --train_file ../dataset/train_op2nl.json \
    --validation_file ../dataset/dev_op2nl.json \
    --source_lang program \
    --target_lang nl \
    --num_train_epochs 20 \
    --checkpointing_steps epoch \
    --per_device_train_batch_size 16 \
    --per_device_eval_batch_size 16 \
    # --dataset_name wmt16 \
    # --dataset_config_name ro-en \