To reproduce our results in the paper, please run the following commands:
1. apt-get update
2. apt-get install ubuntu-make

## WiKiSQL
1. conda env create -f tafv_environment.yml & source /miniconda/etc/profile.d/conda.sh
2. conda activate tafv
3. python -m pip install -r tafv_requirements.txt
4. cd UCTR & sh run_wikisql.sh

## TAT-QA
1. conda env create -f tat_qa_environment.yml & source /miniconda/etc/profile.d/conda.sh
2. conda activate tat-qa & conda install -c conda-forge jsonnet
3. python -m pip install -r tat_qa_requirements.txt & pip install torch==1.9.1+cu111 torchvision==0.10.1+cu111 torchaudio==0.9.1 -f https://download.pytorch.org/whl/torch_stable.html & pip install torch-scatter -f https://data.pyg.org/whl/torch-1.9.1+cu111.html
4. cd UCTR & sh run_tatqa.sh

## SEM-TAB-FACTS
1. conda env create -f tafv_environment.yml & source /miniconda/etc/profile.d/conda.sh
2. conda activate tafv
3. python -m pip install -r tafv_requirements.txt & pip install torch-scatter -f https://data.pyg.org/whl/torch-1.9.1+cu111.html
4. cd UCTR & sh run_sem_tab_facts.sh

## FEVEROUS
1. conda env create -f feverous_environment.yml & source /miniconda/etc/profile.d/conda.sh
2. conda activate feverous & python -m pip install -r feverous_requirements.txt & pip --default-timeout=10000 install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.3.0/en_core_web_sm-2.3.0.tar.gz
3. download the db file using `wget -O FEVEROUS/data/feverous-wiki-pages-db.zip https://s3-eu-west-1.amazonaws.com/fever.public/feverous/feverous-wiki-pages-db.zip` and unzip it (~50G).
3. cd UCTR & sh run_feverous.sh