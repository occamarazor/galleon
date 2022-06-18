from typing import TypedDict
from flask import Flask, jsonify, request
from common import NODE_PORTS, NODE_HOST, BLOCK_TRANSACTIONS, TRANSACTION_KEYS, SUCCESS_REQUEST_STATUS,\
    BAD_REQUEST_STATUS
from build_node import Node, create_node, sync_nodes
from build_blockchain import BLOCK_REWARD, Block, proof_of_work, hash_block, create_block, is_chain_valid
from build_transaction import Transaction, create_transaction

NODE_PORT = NODE_PORTS[0]


class AddTransactionResponse(TypedDict):
    new_transaction: Transaction
    updated_nodes: list[int]


class MineBlockResponse(TypedDict):
    new_block: Block
    updated_nodes: list[int]


def create_app(node_port: int) -> None:
    # Create webapp
    app = Flask(__name__)

    # Create node
    node: Node = create_node(node_port)

    # Request node
    @app.route('/get_node', methods=['GET'])
    def get_node():
        return jsonify(node), SUCCESS_REQUEST_STATUS

    # Validate node chain
    @app.route('/validate_chain', methods=['GET'])
    def validate_chain():
        is_blockchain_valid: bool = is_chain_valid(node['chain'])

        if is_blockchain_valid:
            response: str = 'Chain valid'
        else:
            response: str = 'Chain invalid'
        return response, SUCCESS_REQUEST_STATUS

    # Add new transaction to mempool
    @app.route('/add_transaction', methods=['POST'])
    def add_transaction():
        transaction_json: Transaction = request.get_json()

        # TODO: validate transaction
        if all(key in transaction_json for key in TRANSACTION_KEYS):
            transaction: Transaction = create_transaction(transaction_json['sender'],
                                                          transaction_json['receiver'],
                                                          transaction_json['amount'])
            # Update node mempool
            node['mempool'].append(transaction)
            # Sync all mempool instances
            updated_nodes: list[int] = sync_nodes(node['port'], node['mempool'])
            # Return add_transaction response
            response: AddTransactionResponse = {'new_transaction': transaction, 'updated_nodes': updated_nodes}
            return jsonify(response), SUCCESS_REQUEST_STATUS
        else:
            return 'Transaction data is invalid', BAD_REQUEST_STATUS

    # Mine new block
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
        # Sync all node instances
        updated_nodes: list[int] = sync_nodes(node['port'], node['mempool'], node['chain'])
        # Return mine_block response
        response: MineBlockResponse = {'new_block': new_block, 'updated_nodes': updated_nodes}
        return jsonify(response), SUCCESS_REQUEST_STATUS

    # Update mempool with the latest instance
    @app.route('/update_node', methods=['POST'])
    def update_node():
        mempool_json: list[Transaction] = request.get_json()['mempool']
        chain_json: list[Block] = request.get_json()['chain']
        # TODO: validate mempool
        node['mempool'] = mempool_json
        print(f'Node:{node["port"]} mempool updated: {node["mempool"]}')

        # Validate chain
        if chain_json and is_chain_valid(chain_json):
            node['chain'] = chain_json
            print(f'Node:{node["port"]} chain updated: {node["chain"]}')

        return jsonify(node['mempool']), SUCCESS_REQUEST_STATUS

    # Run flask app
    app.run(host=NODE_HOST, port=node_port)


create_app(NODE_PORT)
