sudo apt update
sudo apt install -y git tmux
mkdir gemma_fine_tuning
cd gemma_fine_tuning/
python3 -m venv venv
tmux new -s training
source venv/bin/activate
/root/gemma_fine_tuning/venv/bin/python3 -m pip install --upgrade pip
pip install packaging
pip install wheel
pip install torch
pip3 install -r requirements.txt
clear
HF_TOKEN='' python3 run_inference.py


tmux attach -t training
