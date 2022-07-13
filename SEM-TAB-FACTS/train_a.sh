# export CUDA_VISIBLE_DEVICES=4
#tf_stf
# python train_task_a/tapas_tf_stf.py -n 0531_bs32_wo_classifier

#tf transfer
# python train_task_a/tapas_tf_stf.py -n 0605_tf_meta+train

# #unsupervised
# python train_task_a/tapas_stf.py -n 0616_stf_eq_count_on_man_reproduce_to_ensure > 0616_stf_eq_count_on_man_reproduce_to_ensure.log

# stf
# python train_task_a/tapas_stf.py -n 0705_stf_50 > 0705_stf_50.log

#aug_50
# python train_task_a/tapas_stf.py -n 0705_stf_50_aug > 0705_stf_50_aug.log


# aug
# python train_task_a/tapas_stf.py -n 0705_stf_aug > 0705_stf_aug.log


# python train_task_a/tapas_stf_syn.py -n 0704_stf_syn > 0704_stf_syn.log


#tf directly
python train_task_a/tapas_tf.py -n tmp
