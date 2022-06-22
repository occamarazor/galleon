from pprint import pprint
from typing import TypedDict
from flask import Flask, jsonify, request
from common import NODE_PORTS, NODE_HOST, MAX_BLOCK_TRANSACTIONS, SUCCESS_REQUEST_STATUS, BAD_REQUEST_STATUS
from build_node import Node, create_node, broadcast_block
from build_blockchain import BLOCK_REWARD, InitialBlock, Block, create_initial_block, proof_of_work, \
    compute_initial_block_target, compute_initial_block_difficulty, update_initial_block, validate_block
from build_transaction import InitialTransaction, Transaction, create_coinbase_transaction, create_transaction, \
    validate_transaction

NODE_PORT = NODE_PORTS[0]


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

    # Add new transaction to node mempool
    @app.route('/add_transaction', methods=['POST'])
    def add_transaction():
        new_transaction_json: InitialTransaction = request.get_json()
        # Create transaction with ID
        new_transaction: Transaction = create_transaction(new_transaction_json)
        # Validate transaction
        is_new_transaction_valid: bool = validate_transaction(new_transaction)

        if is_new_transaction_valid:
            # Add new transaction to mempool
            node['mempool'].append(new_transaction)
            # Return add_transaction response
            return jsonify(new_transaction), SUCCESS_REQUEST_STATUS
        else:
            return 'Transaction data invalid', BAD_REQUEST_STATUS

    # Mine new block
    @app.route('/mine_block', methods=['GET'])
    def mine_block():
        node_address: str = f'Node:{node_port}'
        miner_address: str = f'Miner:{node_port}'
        # Get prev block hash
        prev_block: Block = node['chain'][-1]
        prev_block_hash: str = prev_block['hash']
        # Select new block transactions
        coinbase_transaction: Transaction = create_coinbase_transaction(node_address, miner_address, BLOCK_REWARD)
        block_transactions: list[Transaction] = [coinbase_transaction]
        block_transactions.extend(node['mempool'][:MAX_BLOCK_TRANSACTIONS])
        # Create initial block
        initial_block: InitialBlock = create_initial_block(len(node['chain']), prev_block_hash, block_transactions)
        # Compute initial block target
        initial_block_target: str = compute_initial_block_target(initial_block['bits'])
        # Compute new block hash & nonce
        new_block_hash, new_block_nonce = proof_of_work(initial_block, initial_block_target)
        # Compute new block difficulty
        new_block_difficulty: float = compute_initial_block_difficulty(initial_block_target)
        # Update initial block with hash, nonce & difficulty
        new_block: Block = update_initial_block(initial_block, new_block_hash, new_block_nonce, new_block_difficulty)
        # Add new block to chain
        # TODO: exclude current node
        # node['chain'].append(new_block)
        # Remove block transactions from mempool
        # TODO: exclude current node
        # block_transactions_ids: list[str] = list(map(lambda t: t['id'], new_block['transactions']))[1:]
        # node['mempool'] = list(filter(lambda t: t['id'] not in block_transactions_ids, node['mempool']))
        # Broadcasts new block across network
        updated_nodes: list[int] = broadcast_block(node['port'], new_block)
        # Return mine_block response
        response: MineBlockResponse = {'new_block': new_block, 'updated_nodes': updated_nodes}
        return jsonify(response), SUCCESS_REQUEST_STATUS

    # Add new block to chain
    @app.route('/add_block', methods=['POST'])
    def add_block():
        prev_block: Block = node['chain'][-1]
        prev_block_hash: str = prev_block['hash']
        new_block: Block = request.get_json()
        # Validate new mined block
        is_new_block_valid = validate_block(prev_block_hash, new_block)

        if is_new_block_valid:
            # Add new block to chain
            node['chain'].append(new_block)
            # Remove block transactions from mempool
            block_transactions_ids: list[str] = list(map(lambda t: t['id'], new_block['transactions']))[1:]
            node['mempool'] = list(filter(lambda t: t['id'] not in block_transactions_ids, node['mempool']))
            # Log node updates
            print(f'Node:{node["port"]} chain updated with new block:')
            pprint(new_block)
            print(f'Node:{node["port"]} mempool cleared of transactions: {block_transactions_ids}')
            return jsonify(new_block), SUCCESS_REQUEST_STATUS
        else:
            print(f'Node:{node["port"]} chain update failed, new block invalid:')
            pprint(new_block)
            return 'New block invalid', BAD_REQUEST_STATUS

    # Run flask app
    app.run(debug=True, host=NODE_HOST, port=node_port)


create_app(NODE_PORT)
