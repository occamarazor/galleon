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


def sync_nodes(node_port: int,
               node_prop: list[Transaction] | list[Block],
               update_route: str,
               function_name: str) -> list[int]:
    """ Syncs a specific node prop instance
    :param node_port: current node port
    :param node_prop: current node mempool or chain
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


def sync_mempools(node_port: int, node_mempool: list[Transaction]) -> list[int]:
    """ Syncs all mempool instances
    :param node_port: current node port
    :param node_mempool: current node mempool
    :return: updated nodes
    """
    return sync_nodes(node_port, node_mempool, 'update_mempools', 'sync_mempools')


def sync_chains(node_port: int, node_chain: list[Block]) -> list[int]:
    """ Syncs all mempool instances
    :param node_port: current node port
    :param node_chain: current node chain
    :return: updated nodes
    """
    return sync_nodes(node_port, node_chain, 'update_chains', 'sync_chains')
