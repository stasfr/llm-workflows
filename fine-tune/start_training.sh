#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Starting Setup and Training Script ---"

# Prompt for Hugging Face Token
echo -n "Please enter your Hugging Face Token (it will not be displayed): "
read -s HF_TOKEN
echo

if [ -z "$HF_TOKEN" ]; then
    echo "Error: Hugging Face Token cannot be empty."
    exit 1
fi

# 1. Install dependencies
echo "Updating packages and installing tmux..."
sudo apt update
sudo apt install -y tmux python3-venv

# 2. Create directory and copy files
echo "Setting up the 'fine_tune_gemma' directory..."
mkdir -p fine_tune_gemma
cp fine-tune/requirements.txt fine_tune_gemma/
cp fine-tune/fine_tune_gemma.py fine_tune_gemma/

# 3. Navigate into the directory
cd fine_tune_gemma

# 4. Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# 5. Start training in a new tmux session
SESSION_NAME="training"

if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "A tmux session named '$SESSION_NAME' is already running."
    echo "Please stop it first ('tmux kill-session -t $SESSION_NAME') or attach to it ('tmux attach -t $SESSION_NAME')."
else
    echo "Starting training in a new detached tmux session named '$SESSION_NAME'..."
    # The command to run inside tmux: activate venv, install requirements, and run python script with the HF_TOKEN
    CMD="source venv/bin/activate && pip3 install -r requirements.txt && HF_TOKEN='$HF_TOKEN' python3 fine_tune_gemma.py"
    tmux new-session -d -s $SESSION_NAME "$CMD"

    echo "---"
    echo "✅ Setup complete and training started!"
    echo "A tmux session named 'training' has been created."
    echo "To monitor the progress, attach to the session with the command:"
    echo "   tmux attach -t training"
    echo "To detach from the session, press Ctrl+B then D."
fi
