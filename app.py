from typing import TypedDict, Final
from flask import Flask, jsonify
from blockchain import SUCCESS_REQUEST_STATUS, Transaction, Block, create_blockchain, create_block, proof_of_work,\
    is_chain_valid, hash_block, create_transaction

from uuid import uuid4

MINER_NAME: Final = 'Miner'
MINER_REWARD: Final = 1


class GetBlockchainResponse(TypedDict):
    blockchain: list[Block]
    length: int


class ValidateBlockchainResponse(TypedDict):
    message: str


# Create webapp & blockchain
app = Flask(__name__)

# Create first node address
node_address = str(uuid4()).replace('-', '')

# Create blockchain & mempool
blockchain: list[Block] = create_blockchain()
blockchain_mempool: list[Transaction] = []


# Mine a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    prev_block: Block = blockchain[-1]
    prev_block_nonce: int = prev_block['nonce']
    new_block_nonce: int = proof_of_work(prev_block_nonce)
    prev_block_hash: str = hash_block(prev_block)

    coinbase_transaction: Transaction = create_transaction(node_address, MINER_NAME, MINER_REWARD)
    blockchain_mempool.append(coinbase_transaction)

    # TODO: select block transactions from mempool
    new_block: Block = create_block(len(blockchain), prev_block_hash, new_block_nonce, blockchain_mempool)
    blockchain.append(new_block)

    return jsonify(new_block), SUCCESS_REQUEST_STATUS


# Request the whole blockchain
@app.route('/get_blockchain', methods=['GET'])
def get_blockchain():
    response: GetBlockchainResponse = {'blockchain': blockchain,
                                       'length': len(blockchain)
                                       }

    return jsonify(response), SUCCESS_REQUEST_STATUS


# Validate blockchain
@app.route('/validate_blockchain', methods=['GET'])
def validate_blockchain():
    is_blockchain_valid: bool = is_chain_valid(blockchain)

    if is_blockchain_valid:
        response: ValidateBlockchainResponse = {'message': 'Blockchain valid'}
    else:
        response: ValidateBlockchainResponse = {'message': 'Blockchain invalid'}

    return jsonify(response), SUCCESS_REQUEST_STATUS


# Run flask app
app.run()
