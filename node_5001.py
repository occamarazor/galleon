from typing import TypedDict
from flask import Flask, jsonify, request
from common import NODE_PORTS, NODE_HOST, MAX_BLOCK_TRANSACTIONS, SUCCESS_REQUEST_STATUS, BAD_REQUEST_STATUS
from build_node import Node, create_node, broadcast_transaction, broadcast_block
from build_blockchain import BLOCK_REWARD, InitialBlock, Block, create_initial_block, proof_of_work,\
    compute_initial_block_target, compute_initial_block_difficulty, update_initial_block, validate_block
from build_transaction import Transaction, create_coinbase_transaction, validate_transaction

NODE_PORT = NODE_PORTS[0]


class AddTransactionResponse(TypedDict):
    new_transaction: Transaction
    updated_mempools: list[int]


class MineBlockResponse(TypedDict):
    new_block: Block
    updated_chains: list[int]


def create_app(node_port: int) -> None:
    # Create webapp
    app = Flask(__name__)

    # Create node
    node: Node = create_node(node_port)

    # Request node
    @app.route('/get_node', methods=['GET'])
    def get_node():
        return jsonify(node), SUCCESS_REQUEST_STATUS

    # Add new transaction to mempool
    @app.route('/add_transaction', methods=['POST'])
    def add_transaction():
        new_transaction_json: Transaction = request.get_json()
        # Validate transaction
        is_new_transaction_valid: bool = validate_transaction(new_transaction_json)

        if is_new_transaction_valid:
            # Update node mempool
            # TODO: exclude current node
            # node['mempool'].append(new_transaction_json)
            # Broadcasts new transaction across network
            updated_mempools: list[int] = broadcast_transaction(node['port'], new_transaction_json)
            # Return add_transaction response
            response: AddTransactionResponse = {'new_transaction': new_transaction_json,
                                                'updated_mempools': updated_mempools
                                                }
            return jsonify(response), SUCCESS_REQUEST_STATUS
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
        # TODO: prev_block_height & prev_block_hash instead of chain len
        initial_block: InitialBlock = create_initial_block(len(node['chain']), prev_block_hash, block_transactions)
        # Compute initial block target
        initial_block_target: str = compute_initial_block_target(initial_block['bits'])
        # Compute new block hash & nonce
        new_block_hash, new_block_nonce = proof_of_work(initial_block, initial_block_target)
        # Compute new block difficulty
        new_block_difficulty: float = compute_initial_block_difficulty(initial_block_target)
        # Update new initial block with hash & nonce
        new_block: Block = update_initial_block(initial_block, new_block_hash, new_block_nonce, new_block_difficulty)
        # Add new block to chain
        # TODO: exclude current node
        # node['chain'].append(new_block)
        # Remove mined transactions from mempool
        # TODO: exclude current node
        # node['mempool'] = node['mempool'][MAX_BLOCK_TRANSACTIONS:]
        # Broadcasts new block across network
        updated_chains: list[int] = broadcast_block(node['port'], new_block)
        # Return mine_block response
        response: MineBlockResponse = {'new_block': new_block, 'updated_chains': updated_chains}
        return jsonify(response), SUCCESS_REQUEST_STATUS

    # TODO: consensus route for indirect use
    # Update node mempool with new transaction (сonsensus route for indirect use)
    @app.route('/update_mempool', methods=['POST'])
    def update_mempool():
        new_transaction_json: Transaction = request.get_json()
        is_new_transaction_valid: bool = validate_transaction(new_transaction_json)

        # Validate new transaction
        if is_new_transaction_valid:
            node['mempool'].append(new_transaction_json)
            print(f'Node:{node["port"]} mempool updated with new transaction: {new_transaction_json}')
            return jsonify(new_transaction_json), SUCCESS_REQUEST_STATUS
        else:
            return 'New transaction invalid', BAD_REQUEST_STATUS

    # Update node chains with the latest chain (сonsensus route for indirect use)
    @app.route('/update_chain', methods=['POST'])
    def update_chain():
        prev_block: Block = node['chain'][-1]
        prev_block_hash: str = prev_block['hash']
        new_block_json: Block = request.get_json()
        is_new_block_valid = validate_block(prev_block_hash, new_block_json)

        # Validate new mined block
        if is_new_block_valid:
            node['chain'].append(new_block_json)
            node['mempool'] = node['mempool'][MAX_BLOCK_TRANSACTIONS:]
            print(f'Node:{node["port"]} chain updated with new block: {new_block_json}')
            return jsonify(new_block_json), SUCCESS_REQUEST_STATUS
        else:
            print(f'Node:{node["port"]} chain update failed, new block invalid: {new_block_json}')
            return 'New block invalid', BAD_REQUEST_STATUS

    # Run flask app
    app.run(debug=True, host=NODE_HOST, port=node_port)


create_app(NODE_PORT)
