import json
from hashlib import sha256
from typing import TypedDict, Final
from datetime import datetime

from urllib.parse import urlparse
import requests
from requests import Response

TARGET_ZEROS: Final = '0000'
INITIAL_PREV_BLOCK_HASH: Final = '0'
INITIAL_BLOCK_NONCE: Final = 1
SUCCESS_REQUEST_STATUS: Final = 200

MINER_NAME: Final = 'Miner'
BLOCK_REWARD: Final = 1
BLOCK_TRANSACTIONS: Final = 10

# Build blockchain
class Transaction(TypedDict):
    sender: str
    receiver: str
    amount: float


class Block(TypedDict):
    timestamp: str
    height: int
    prev_hash: str
    nonce: int
    transactions: list[Transaction]


def calc_block_hash(block_nonce: int, prev_block_nonce: int) -> str:
    """ Computes possible block hash solving a simple cryptographic puzzle
    :param block_nonce: possible golden nonce
    :param prev_block_nonce: previous block nonce
    :return: possible block hash
    """
    return sha256(f'{block_nonce ** 2 - prev_block_nonce ** 2}'.encode()).hexdigest()


def hash_block(block: Block) -> str:
    """ Hashes entire block
    :param block: block
    :return: block hash
    """
    encoded_block = json.dumps(block, sort_keys=True).encode()
    return sha256(encoded_block).hexdigest()


def is_chain_valid(chain: list[Block]) -> bool:
    """ Validates the entire blockchain
    :param chain: blockchain
    :return: boolean validation result
    """
    block_height: int = 1

    # Validate each block
    while block_height < len(chain):
        # Prev & current blocks hashes validation
        prev_block: Block = chain[block_height - 1]
        current_block: Block = chain[block_height]

        if hash_block(prev_block) != current_block['prev_hash']:
            return False

        # Current block hash validation
        prev_block_nonce: int = prev_block['nonce']
        current_block_nonce: int = current_block['nonce']
        current_block_hash: str = calc_block_hash(current_block_nonce, prev_block_nonce)

        if current_block_hash[:4] != TARGET_ZEROS:
            return False

        block_height += 1
    return True


def proof_of_work(prev_block_nonce: int) -> int:
    """ Solves the cryptographic puzzle
    :param prev_block_nonce: previous block nonce
    :return: new block nonce
    """
    new_block_nonce: int = INITIAL_BLOCK_NONCE
    nonce_is_valid: bool = False

    # Compute hashes until golden nonce found
    while nonce_is_valid is False:
        possible_hash: str = calc_block_hash(new_block_nonce, prev_block_nonce)

        if possible_hash[:4] == TARGET_ZEROS:
            nonce_is_valid = True
        else:
            new_block_nonce += 1

    return new_block_nonce


def create_block(blockchain_length: int,
                 prev_block_hash: str,
                 new_block_nonce: int,
                 transactions: list[Transaction]) -> Block:
    """ Creates a new block with data
    :param blockchain_length: blockchain length
    :param prev_block_hash: previous block hash
    :param new_block_nonce: new block nonce
    :param transactions: block transactions
    :return: new block
    """
    return {'timestamp': f'{datetime.now()}',
            'height': blockchain_length + 1,
            'prev_hash': prev_block_hash,
            'nonce': new_block_nonce,
            'transactions': transactions
            }


def create_blockchain() -> list[Block]:
    """ Creates a new blockchain with genesis block
    :return: blockchain
    """
    new_blockchain: list[Block] = []
    # TODO: init node address
    coinbase_transaction: Transaction = create_transaction('111', MINER_NAME, BLOCK_REWARD)
    # TODO: init nodes
    nodes: set[str] = set()
    genesis_block: Block = create_block(len(new_blockchain), INITIAL_PREV_BLOCK_HASH, INITIAL_BLOCK_NONCE, [coinbase_transaction])
    new_blockchain.append(genesis_block)
    return new_blockchain


# Crypto stuff
def create_transaction(sender: str, receiver: str, amount: float) -> Transaction:
    """ Creates a new transaction with data
    :param sender: transaction sender
    :param receiver: transaction receiver
    :param amount: transaction amount
    :return: new transaction
    """
    return {'sender': sender,
            'receiver': receiver,
            'amount': amount
            }


def create_node(url: str) -> str:
    """ Creates a node netloc from a url address
    :param url: url address
    :return: node netloc
    """
    parsed_url = urlparse(url)
    return parsed_url.netloc


def replace_chain(current_chain: list[Block], chain_nodes: set[str]) -> tuple[bool, list[Block]]:
    """ Gets longest chain from all nodes
    :param current_chain: current blockchain
    :param chain_nodes: current blockchain nodes
    :return: replace status & current blockchain longest chain
    """
    longest_chain: list[Block] | None = None
    max_chain_length: int = len(current_chain)

    for node in chain_nodes:
        response: Response = requests.get(f'http://{node}/get_blockchain')

        if response.status_code == SUCCESS_REQUEST_STATUS:
            node_chain_length: int = response.json()['length']
            node_chain: list[Block] = response.json()['blockchain']

            if node_chain_length > max_chain_length and is_chain_valid(node_chain):
                max_chain_length = node_chain_length
                longest_chain = node_chain

    if longest_chain:
        return True, longest_chain
    return False, longest_chain
