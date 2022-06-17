from typing import TypedDict, Final
from flask import Flask, jsonify, request
from common import NODE_PORTS, NODE_HOST, BLOCK_TRANSACTIONS, TRANSACTION_KEYS, SUCCESS_REQUEST_STATUS,\
    BAD_REQUEST_STATUS
from build_node import Node, create_node, find_longest_chain
from build_blockchain import BLOCK_REWARD, Block, proof_of_work, hash_block, create_block, is_chain_valid
from build_transaction import Transaction, create_transaction


class GetChainResponse(TypedDict):
    chain: list[Block]
    length: int


class ReplaceBlockchainResponse(TypedDict):
    message: str
    new_chain: list[Block] | None


def create_app(node_port: int) -> None:
    node: Node = create_node(node_port)

    # Create webapp
    app = Flask(__name__)

    # Request node
    @app.route('/get_node', methods=['GET'])
    def get_node():
        return jsonify(node), SUCCESS_REQUEST_STATUS

    # Request node chain
    @app.route('/get_chain', methods=['GET'])
    def get_chain():
        node_chain: list[Block] = node['chain']
        response: GetChainResponse = {'chain': node_chain, 'length': len(node_chain)}
        return jsonify(response), SUCCESS_REQUEST_STATUS

    # Validate chain
    @app.route('/validate_chain', methods=['GET'])
    def validate_chain():
        is_blockchain_valid: bool = is_chain_valid(node['chain'])

        if is_blockchain_valid:
            response: str = 'Chain valid'
        else:
            response: str = 'Chain invalid'
        return response, SUCCESS_REQUEST_STATUS

    # Adds transaction to mempool
    @app.route('/add_transaction', methods=['POST'])
    def add_transaction():
        transactions_json = request.get_json()

        if all(key in transactions_json for key in TRANSACTION_KEYS):
            transaction: Transaction = create_transaction(transactions_json['sender'],
                                                          transactions_json['receiver'],
                                                          transactions_json['amount'])
            node['mempool'].append(transaction)
            # TODO: Sync all mempools
            return jsonify(transaction), SUCCESS_REQUEST_STATUS
        else:
            return 'Transaction data is invalid', BAD_REQUEST_STATUS

    # Mine a new block
    @app.route('/mine_block', methods=['GET'])
    def mine_block():
        node_address: str = f'Node:{node_port}'
        miner_address: str = f'Miner:{node_port}'

        # Compute prev block hash & new block nonce
        prev_block: Block = node['chain'][-1]
        prev_block_nonce: int = prev_block['nonce']
        new_block_nonce: int = proof_of_work(prev_block_nonce)
        prev_block_hash: str = hash_block(prev_block)
        # Select new block transactions
        coinbase_transaction: Transaction = create_transaction(node_address, miner_address, BLOCK_REWARD)
        block_transactions = [coinbase_transaction]
        block_transactions.extend(node['mempool'][:BLOCK_TRANSACTIONS])
        # Create new block & add it to chain
        new_block: Block = create_block(len(node['chain']), prev_block_hash, new_block_nonce, block_transactions)
        node['chain'].append(new_block)
        # Remove mined transactions from mempool
        node['mempool'] = node['mempool'][BLOCK_TRANSACTIONS:]
        # TODO: Sync all mempools
        # TODO: Sync all chains

        return jsonify(new_block), SUCCESS_REQUEST_STATUS

    # Replace current chain with the logest chain
    @app.route('/replace_chain', methods=['GET'])
    def replace_chain():
        is_chain_replaced, longest_chain = find_longest_chain(node['chain'])

        if is_chain_replaced:
            node['chain'] = longest_chain
            response: ReplaceBlockchainResponse = {'message': 'The current chain was replaced', 'new_chain': node['chain']}
        else:
            response: ReplaceBlockchainResponse = {'message': 'The current chain is the largest', 'new_chain': None}
        return jsonify(response), SUCCESS_REQUEST_STATUS

    # Run flask app
    app.run(host=NODE_HOST, port=node_port)


create_app(NODE_PORTS[0])
