from flask import Flask, jsonify
from blockchain import Block, GetBlockchainResponse, create_blockchain, create_block, proof_of_work, is_chain_valid, \
    hash_block

SUCCESS_REQUEST_STATUS = 200

# Create webapp & blockchain
app = Flask(__name__)
blockchain: list[Block] = create_blockchain()


# Mine a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    prev_block: Block = blockchain[-1]
    prev_block_nonce: int = prev_block['nonce']
    new_block_nonce: int = proof_of_work(prev_block_nonce)
    prev_block_hash: str = hash_block(prev_block)
    new_block: Block = create_block(len(blockchain), new_block_nonce, prev_block_hash)
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
        response = {'message': 'Blockchain valid'}
    else:
        response = {'message': 'Blockchain invalid'}

    return jsonify(response), SUCCESS_REQUEST_STATUS


# Run flask app
app.run()
