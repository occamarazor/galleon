import json
from hashlib import sha256
from typing import TypedDict, Final
from datetime import datetime
from build_transaction import Transaction, create_transaction

TARGET_ZEROS: Final = '0000'
INITIAL_PREV_BLOCK_HASH: Final = '0'
INITIAL_BLOCK_NONCE: Final = 1
BLOCK_REWARD: Final = 1


# Build blockchain
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
    """ Validates the entire chain
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


def create_chain(node_address: str, miner_address: str) -> list[Block]:
    """ Creates a new chain with genesis block
    :param node_address: node address
    :param miner_address: miner address
    :return: chain
    """
    new_chain: list[Block] = []
    coinbase_transaction: Transaction = create_transaction(node_address, miner_address, BLOCK_REWARD)
    genesis_block: Block = create_block(len(new_chain),
                                        INITIAL_PREV_BLOCK_HASH,
                                        INITIAL_BLOCK_NONCE,
                                        [coinbase_transaction])
    new_chain.append(genesis_block)
    return new_chain
