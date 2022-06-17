from typing import TypedDict
import requests
from requests import Response
from common import NODE_PORTS, SUCCESS_REQUEST_STATUS
from build_blockchain import Block, create_chain, is_chain_valid
from build_transaction import Transaction


# Build node
class Node(TypedDict):
    port: int
    mempool: list[Transaction]
    chain: list[Block]


def create_node(port: int) -> Node:
    node_address: str = f'Node:{port}'
    miner_address: str = f'Miner:{port}'
    node_chain = create_chain(node_address, miner_address)
    return {'port': port, 'mempool': [], 'chain': node_chain}


def find_longest_chain(current_chain: list[Block]) -> tuple[bool, list[Block]]:
    longest_chain: list[Block] | None = None
    max_chain_length: int = len(current_chain)

    for node_port in NODE_PORTS:
        response: Response = requests.get(f'http://127.0.0.1:{node_port}/get_chain')

        if response.status_code == SUCCESS_REQUEST_STATUS:
            node_chain_length: int = response.json()['length']
            node_chain: list[Block] = response.json()['chain']

            if node_chain_length > max_chain_length and is_chain_valid(node_chain):
                max_chain_length = node_chain_length
                longest_chain = node_chain

    if longest_chain:
        return True, longest_chain
    return False, longest_chain
