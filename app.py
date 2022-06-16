import json
from typing import TypedDict
from flask import Flask, jsonify, request
from blockchain import SUCCESS_REQUEST_STATUS, BAD_REQUEST_STATUS, MINER_NAME, BLOCK_REWARD, BLOCK_TRANSACTIONS,\
    Transaction, Block, create_blockchain, create_block, proof_of_work, is_chain_valid, hash_block, create_transaction

from uuid import uuid4

TRANSACTION_KEYS = ['sender', 'receiver', 'amount']


class GetBlockchainResponse(TypedDict):
    blockchain: list[Block]
    length: int


class ValidateBlockchainResponse(TypedDict):
    message: str


# Create webapp & blockchain
app = Flask(__name__)

# TODO: each node has its own address & mempool
# Create first node address, blockchain & mempool
node_address: str = str(uuid4()).replace('-', '')
blockchain: list[Block] = create_blockchain(node_address)
blockchain_mempool: list[Transaction] = []


# Mine a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    prev_block: Block = blockchain[-1]
    prev_block_nonce: int = prev_block['nonce']
    new_block_nonce: int = proof_of_work(prev_block_nonce)
    prev_block_hash: str = hash_block(prev_block)

    coinbase_transaction: Transaction = create_transaction(node_address, MINER_NAME, BLOCK_REWARD)
    block_transactions = [coinbase_transaction]
    block_transactions.extend(blockchain_mempool[:BLOCK_TRANSACTIONS])

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


# Adds transaction to mempool
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    transactions_json = request.get_json()

    if all(key in transactions_json for key in TRANSACTION_KEYS):
        transaction: Transaction = create_transaction(transactions_json['sender'],
                                         transactions_json['receiver'],
                                         transactions_json['amount'])
        blockchain_mempool.append(transaction)
        return jsonify(transaction), SUCCESS_REQUEST_STATUS
    else:
        return 'Some transaction props are missing', BAD_REQUEST_STATUS


# Run flask app
app.run()
