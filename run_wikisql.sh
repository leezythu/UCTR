export CUDA_VISIBLE_DEVICES=0
cd WiKiSQL/Table-Pretraining/examples/
export PYTHONPATH=.. 
# sh process.sh
sh train_syn.sh
sh eval.sh