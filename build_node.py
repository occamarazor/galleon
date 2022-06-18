from typing import TypedDict
import requests
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
    node_chain = create_chain(node_address, miner_address)
    return {'port': node_port, 'mempool': [], 'chain': node_chain}


def sync_mempools(node_port: int, node_mempool: list[Transaction]) -> list[int]:
    updated_nodes: list[int] = []
    # TODO: exclude current node
    print(f'Current node: Node:{node_port}')
    for node_port in NODE_PORTS:
        try:
            response: Response = requests.post(f'http://127.0.0.1:{node_port}/update_mempool', json=node_mempool)

            if response.status_code == SUCCESS_REQUEST_STATUS:
                updated_nodes.append(node_port)
        except RequestException as err:
            print(f'Node Request Error: node:{node_port} unavailable')
            print(repr(err))

    return updated_nodes
