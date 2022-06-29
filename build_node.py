import requests
from typing import TypedDict
from requests import Response, RequestException
from common import NODE_PORTS, SUCCESS_REQUEST_STATUS
from build_blockchain import Block, create_chain
from build_transaction import Transaction


# Build node
class Node(TypedDict):
    port: int
    mempool: list[Transaction]
    chain: list[Block]


def create_node(node_port: int) -> Node:
    """ Creates a new node with data
    :param node_port: node port
    :return: new node
    """
    node_address: str = f'Node:{node_port}'
    miner_address: str = f'Miner:{node_port}'
    node_chain: list[Block] = create_chain(node_address, miner_address)
    return {'port': node_port, 'mempool': [], 'chain': node_chain}


def broadcast_block(broadcast_node: int, new_block: Block) -> list[int]:
    """ Broadcasts new mined block across entire network
    :param broadcast_node: current node port
    :param new_block: new mined block
    :return: updated nodes
    """
    updated_nodes: list[int] = []

    for node_port in NODE_PORTS:
        if node_port != broadcast_node:
            try:
                response: Response = requests.post(f'http://127.0.0.1:{node_port}/add_block', json=new_block)

                if response.status_code == SUCCESS_REQUEST_STATUS:
                    updated_nodes.append(node_port)
            except RequestException as err:
                print(f'broadcast_block error: node:{node_port} unavailable')
                print(repr(err))

    return updated_nodes


def update_node(node: Node, new_block: Block) -> None:
    """ Updates node's chain & mempool
    :param node: node
    :param new_block: new block
    :return: None
    """
    # Add new block to chain
    node['chain'].append(new_block)
    # Remove block transactions from mempool
    block_transactions_ids: list[str] = list(map(lambda t: t['id'], new_block['transactions']))[1:]
    node['mempool'] = list(filter(lambda t: t['id'] not in block_transactions_ids, node['mempool']))
