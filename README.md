# Galleon - a simple POW blockchain showcase
###### Overview: Run nodes, add transactions, mine blocks

## Runbook
#### Set Environment
- Install Homebrew package manager  
    `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`  
- Update and upgrade Homebrew (if needed)  
    `brew update && brew upgrade && brew cleanup`  
- Install pyenv  
    `brew install pyenv`  
- Install python 3.10.4  
    `pyenv install 3.10.4`  
- Install python global version  
    `pyenv global 3.10.4`  
- Install python local version  
    `cd ~/path/to/project`  
    `pyenv local 3.10.4`
- Install pipenv  
    `brew install pipenv`  
- Create project venv with all project dependencies  
    `cd ~/path/to/project`  
    `pipenv install --python 3.10.4`  
- Add venv to current project  

#### Run nodes
- Activate project venv  
    `pipenv shell`  
- Start nodes in separate terminals  
    `python node_5001.py`  
    `python node_5002.py`  
    `python node_5003.py`  


#### Interact
- Request node info  
    `GET http://127.0.0.1:5001/get_node`  
  - Node chain  
  - Node mempool  
  - Node port  
- Add new transaction to node's mempool  
    `POST http://127.0.0.1:5001/add_transaction`  
    `BODY transaction_new.json`  
  - Generates unique transaction ID  
  - Validates transaction  
  - Validates transaction's inputs/outputs  
  - Adds a valid transaction to node's mempool  
- Add same new transaction to different nodes' mempools  
    `POST http://127.0.0.1:5001/add_transaction`  
    `POST http://127.0.0.1:5002/add_transaction`  
    `POST http://127.0.0.1:5003/add_transaction`  
    `BODY transaction_with_id.json`  
  - Validates transaction  
  - Validates transaction's inputs/outputs
  - Adds a valid transaction to node's mempool  
- Mine new block  
    `GET http://127.0.0.1:5001/mine_block`  
  - Adds coinbase transaction  
  - Adds user transactions (2TX from node's mempool max, FIFO)  
  - Computes current target from bits  
  - Computes block hash & nonce by solving cryptographic puzzle  
  - Computes mining difficulty  
  - Creates new block  
  - Broadcasts new block across whole network  
- Add mined block to node chain (internal route guarded by POW)  
    `POST http://127.0.0.1:5001/add_block`  
    `BODY fake_block.json`  
  - Validates new mined block (you can still play around with fake_block & TRY to bypass POW)  
  - Adds valid mined block to node's chain  
  - Removes valid mined block's transactions from node's mempool (if present)  

