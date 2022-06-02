from flask import Flask, jsonify
from blockchain import Block, GetBlockchainResponse, create_blockchain, proof_of_work, hash_block, \
    create_block

# 2) Create webapp & blockchain
app = Flask(__name__)
blockchain: list[Block] = create_blockchain()


# 3) Mine a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    prev_block: Block = blockchain[-1]
    prev_block_nonce: int = prev_block['nonce']
    new_block_nonce: int = proof_of_work(prev_block_nonce)
    prev_block_hash: str = hash_block(prev_block)
    new_block: Block = create_block(len(blockchain), new_block_nonce, prev_block_hash)
    blockchain.append(new_block)

    return jsonify(new_block), 200


# 4) Request the whole blockchain
@app.route('/get_blockchain', methods=['GET'])
def get_blockchain():
    response: GetBlockchainResponse = {'blockchain': blockchain,
                                       'length': len(blockchain)
                                       }

    return jsonify(response), 200


# 5) Run flask app
app.run()
