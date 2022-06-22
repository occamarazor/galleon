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


def broadcast_transaction(node_port: int, new_transaction: Transaction) -> list[int]:
    """ Broadcasts new transaction across entire network
    :param node_port: current node port
    :param new_transaction: new transaction
    :return: updated nodes
    """
    return update_nodes(node_port, new_transaction, 'update_mempool', 'broadcast_transaction')


def broadcast_block(node_port: int, new_block: Block) -> list[int]:
    """ Broadcasts new mined block across entire network
    :param node_port: current node port
    :param new_block: new mined block
    :return: updated nodes
    """
    return update_nodes(node_port, new_block, 'update_chain', 'broadcast_block')


def update_nodes(node_port: int,
                 node_prop: Transaction | Block,
                 update_route: str,
                 function_name: str) -> list[int]:
    """ Syncs a specific node prop instances
    :param node_port: current node port
    :param node_prop: new transaction or new mined block
    :param update_route: API route for prop update
    :param function_name: function using sync_nodes
    :return: updated nodes
    """
    updated_nodes: list[int] = []
    # TODO: exclude current node
    print(f'Current node: Node:{node_port}')
    for node_port in NODE_PORTS:
        try:
            response: Response = requests.post(f'http://127.0.0.1:{node_port}/{update_route}', json=node_prop)

            if response.status_code == SUCCESS_REQUEST_STATUS:
                updated_nodes.append(node_port)
        except RequestException as err:
            print(f'{function_name} error: node:{node_port} unavailable')
            print(repr(err))

    return updated_nodes
