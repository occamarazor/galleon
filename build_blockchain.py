import json
from typing import TypedDict, Final
from datetime import datetime
from hashlib import sha256
from build_transaction import Transaction, create_coinbase_transaction

TARGET_ZEROS: Final = '0000'
INITIAL_PREV_BLOCK_HASH: Final = '0'
INITIAL_BLOCK_HASH: Final = '0'
INITIAL_BLOCK_NONCE: Final = 1
BLOCK_REWARD: Final = 1.1


# Build blockchain
class Block(TypedDict):
    timestamp: str
    height: int
    prev_hash: str
    hash: str
    nonce: int
    transactions: list[Transaction]


def create_chain(node_address: str, miner_address: str) -> list[Block]:
    """ Creates a new chain with genesis block
    :param node_address: node address
    :param miner_address: miner address
    :return: chain
    """
    new_chain: list[Block] = []
    coinbase_transaction: Transaction = create_coinbase_transaction(node_address, miner_address, BLOCK_REWARD)
    genesis_block: Block = create_initial_block(len(new_chain), INITIAL_PREV_BLOCK_HASH, [coinbase_transaction])
    new_chain.append(genesis_block)
    return new_chain


def create_initial_block(blockchain_length: int, prev_block_hash: str, transactions: list[Transaction]) -> Block:
    """ Creates a new block with initial hash & nonce
    :param blockchain_length: blockchain length
    :param prev_block_hash: previous block hash
    :param transactions: initial block transactions
    :return: new initial block
    """
    return {'timestamp': f'{datetime.now()}',
            'height': blockchain_length + 1,
            'prev_hash': prev_block_hash,
            'hash': INITIAL_BLOCK_HASH,
            'nonce': INITIAL_BLOCK_NONCE,
            'transactions': transactions
            }


def proof_of_work(initial_block: Block) -> tuple[str, int]:
    """ Computes block hash & nonce by solving cryptographic puzzle
    :param initial_block: block with initial hash & nonce
    :return: new block hash & nonce
    """
    nonce_is_valid: bool = False
    new_block_hash: str = initial_block['hash']
    new_block_nonce: int = initial_block['nonce']

    # Cycle through possible hashes until golden nonce found
    while nonce_is_valid is False:
        new_block_hash = compute_initial_block_hash(initial_block, new_block_nonce)

        if new_block_hash.startswith(TARGET_ZEROS):
            nonce_is_valid = True
        else:
            new_block_nonce += 1

    return new_block_hash, new_block_nonce


def compute_initial_block_hash(initial_block: Block, block_nonce: int) -> str:
    """ Computes block hash by solving a cryptographic puzzle
    :param initial_block: block with initial hash & nonce
    :param block_nonce: golden nonce
    :return: block hash
    """
    initial_block_hash = hash_initial_block(initial_block)
    return sha256((str(block_nonce) + initial_block_hash).encode()).hexdigest()


def hash_initial_block(initial_block: Block) -> str:
    """ Hashes block with initial hash & nonce
    :param initial_block: block with initial hash & nonce
    :return: hashed block
    """
    encoded_initial_block = json.dumps(initial_block, sort_keys=True).encode()
    return sha256(encoded_initial_block).hexdigest()


def update_block(block: Block, new_block_hash: str, new_block_nonce: int) -> Block:
    """ Updates block with new hash & nonce
    :param block: block
    :param new_block_hash: new block hash
    :param new_block_nonce: new block nonce
    :return: block updated with new hash & nonce
    """
    new_block: Block = {k: v for k, v in block.items()}
    new_block['hash'] = new_block_hash
    new_block['nonce'] = new_block_nonce
    return new_block


def validate_chain(chain: list[Block]) -> bool:
    """ Validates the entire chain
    :param chain: chain
    :return: chain validation status
    """
    block_height: int = 1

    if not chain:
        return False

    # Validate each block
    while block_height < len(chain):
        # Prev & current blocks hashes validation
        prev_block: Block = chain[block_height - 1]
        current_block: Block = chain[block_height]
        prev_block_hash: str = prev_block['hash']
        current_block_prev_hash: str = current_block['prev_hash']

        if prev_block_hash != current_block_prev_hash:
            return False

        # Current block hash validation
        current_block_hash: str = current_block['hash']
        current_block_nonce: int = current_block['nonce']
        current_initial_block: Block = update_block(current_block, INITIAL_BLOCK_HASH, INITIAL_BLOCK_NONCE)
        current_initial_block_hash: str = compute_initial_block_hash(current_initial_block, current_block_nonce)

        if current_block_hash != current_initial_block_hash and not current_initial_block_hash.startswith(TARGET_ZEROS):
            return False

        block_height += 1
    return True
