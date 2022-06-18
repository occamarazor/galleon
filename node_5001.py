from typing import TypedDict
from flask import Flask, jsonify, request
from common import NODE_PORTS, NODE_HOST, BLOCK_TRANSACTIONS, SUCCESS_REQUEST_STATUS, BAD_REQUEST_STATUS
from build_node import Node, create_node, sync_mempools, sync_chains
from build_blockchain import BLOCK_REWARD, Block, proof_of_work, hash_block, create_block, validate_chain
from build_transaction import Transaction, create_coinbase_transaction, validate_transaction, validate_mempool

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
        transaction_json: Transaction = request.get_json()
        # Validate transaction
        is_transaction_valid: bool = validate_transaction(transaction_json)

        if is_transaction_valid:
            # Update node mempool
            node['mempool'].append(transaction_json)
            # Sync all mempool instances
            updated_mempools: list[int] = sync_mempools(node['port'], node['mempool'])
            # Return add_transaction response
            response: AddTransactionResponse = {'new_transaction': transaction_json,
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

        # Compute prev block hash & new block nonce
        prev_block: Block = node['chain'][-1]
        prev_block_nonce: int = prev_block['nonce']
        new_block_nonce: int = proof_of_work(prev_block_nonce)
        prev_block_hash: str = hash_block(prev_block)
        # Select new block transactions
        coinbase_transaction: Transaction = create_coinbase_transaction(node_address, miner_address, BLOCK_REWARD)
        block_transactions: list[Transaction] = [coinbase_transaction]
        block_transactions.extend(node['mempool'][:BLOCK_TRANSACTIONS])
        # Create new block & add it to chain
        new_block: Block = create_block(len(node['chain']), prev_block_hash, new_block_nonce, block_transactions)
        node['chain'].append(new_block)
        # Remove mined transactions from mempool
        node['mempool'] = node['mempool'][BLOCK_TRANSACTIONS:]
        # Sync all chain instances
        updated_chains: list[int] = sync_chains(node['port'], node['chain'])
        # Return mine_block response
        response: MineBlockResponse = {'new_block': new_block, 'updated_chains': updated_chains}
        return jsonify(response), SUCCESS_REQUEST_STATUS

    # Internal route: Update node mempools with the latest mempool
    @app.route('/update_mempools', methods=['POST'])
    def update_mempools():
        mempool_json: list[Transaction] = request.get_json()
        # Validate mempool
        is_mempool_valid: bool = validate_mempool(mempool_json)

        if is_mempool_valid:
            node['mempool'] = mempool_json
            print(f'Node:{node["port"]} mempool updated: {node["mempool"]}')
            return jsonify(node['mempool']), SUCCESS_REQUEST_STATUS
        else:
            return 'Mempool invalid', BAD_REQUEST_STATUS

    # Internal route: Update node chains with the latest chain
    @app.route('/update_chains', methods=['POST'])
    def update_chains():
        chain_json: list[Block] = request.get_json()
        # Validate chain
        if chain_json and validate_chain(chain_json):
            node['chain'] = chain_json
            print(f'Node:{node["port"]} chain updated: {node["chain"]}')
            return jsonify(node['chain']), SUCCESS_REQUEST_STATUS
        else:
            return 'Chain invalid', BAD_REQUEST_STATUS

    # Run flask app
    app.run(debug=True, host=NODE_HOST, port=node_port)


create_app(NODE_PORT)
