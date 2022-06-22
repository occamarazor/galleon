import json
from pprint import pprint
from typing import TypedDict, Final
from datetime import datetime
from decimal import Decimal
from hashlib import sha256
from build_transaction import Transaction, create_coinbase_transaction

BLOCK_REWARD: Final = 1.1
INITIAL_BLOCK_HASH: Final = '0'
INITIAL_BLOCK_NONCE: Final = 1
# TODO: difficulty adjustment - timer/blocks?
INITIAL_BLOCK_BITS: int = 509450204  # 4 leading zeros
MAX_TARGET = '0x00FFFF0000000000000000000000000000000000000000000000000000000000'


# Build blockchain
class InitialBlock(TypedDict):
    height: int
    timestamp: str
    prev_hash: str
    transactions: list[Transaction]
    bits: int


class Block(InitialBlock):
    hash: str
    nonce: int
    difficulty: float


def create_chain(node_address: str, miner_address: str) -> list[Block]:
    """ Creates a new chain with genesis block
    :param node_address: node address
    :param miner_address: miner address
    :return: chain
    """
    new_chain: list[Block] = []
    coinbase_transaction: Transaction = create_coinbase_transaction(node_address, miner_address, BLOCK_REWARD)
    genesis_initial_block: InitialBlock = create_initial_block(len(new_chain),
                                                               INITIAL_BLOCK_HASH,
                                                               [coinbase_transaction])
    genesis_initial_block_target: str = compute_initial_block_target(genesis_initial_block['bits'])
    genesis_block_difficulty: float = compute_initial_block_difficulty(genesis_initial_block_target)
    genesis_block: Block = update_initial_block(genesis_initial_block,
                                                INITIAL_BLOCK_HASH,
                                                INITIAL_BLOCK_NONCE,
                                                genesis_block_difficulty)
    new_chain.append(genesis_block)
    return new_chain


def create_initial_block(blockchain_length: int, prev_block_hash: str, transactions: list[Transaction]) -> InitialBlock:
    """ Creates a new initial block
    :param blockchain_length: blockchain length
    :param prev_block_hash: previous block hash
    :param transactions: block transactions
    :return: new initial block
    """
    return {'height': blockchain_length + 1,
            'timestamp': f'{datetime.now()}',
            'prev_hash': prev_block_hash,
            'transactions': transactions,
            'bits': INITIAL_BLOCK_BITS,
            }


def compute_initial_block_target(bits: int) -> str:
    """ Computes initial block target
    :param bits: target encoded in bits
    :return: hexadecimal target
    """
    bits_in_hex = hex(bits)
    derived_target_start = int(bits_in_hex[2:4], 16)
    derived_target_end = bits_in_hex[4:]
    current_target_start = '0' * (64 - derived_target_start * 2)
    current_target_end = '0' * (derived_target_start * 2 - len(derived_target_end))
    return f'0x{current_target_start}{derived_target_end}{current_target_end}'


def compute_initial_block_difficulty(current_target: str) -> float:
    """ Computes initial block difficulty
    :param current_target: block target
    :return: mining difficulty
    """
    max_target_dec = int(MAX_TARGET, 16)
    current_target_dec = int(current_target, 16)
    return float(round(Decimal(max_target_dec / current_target_dec), 2))


# TODO: more realistic hash computation
#   1. Compute block_header
#     a. client
#     b. timestamp
#     c. transactions: merkle root
#     d. prev_hash
#     e. target
#   2. Compute block_header with nonce
#   3. Find double hash
#   4. Compare double hash with target
def proof_of_work(initial_block: InitialBlock, initial_block_target: str) -> tuple[str, int]:
    """ Computes block hash & nonce by solving cryptographic puzzle
    :param initial_block: initial block
    :param initial_block_target: initial block target
    :return: new block hash, nonce & difficulty
    """
    nonce_is_valid: bool = False
    new_block_hash: str = INITIAL_BLOCK_HASH
    new_block_nonce: int = INITIAL_BLOCK_NONCE

    # Cycle through possible hashes until golden nonce found
    while nonce_is_valid is False:
        new_block_hash = compute_initial_block_hash(initial_block, new_block_nonce)

        if initial_block_target > f'0x{new_block_hash}':
            nonce_is_valid = True
        else:
            new_block_nonce += 1

    return new_block_hash, new_block_nonce


def compute_initial_block_hash(initial_block: InitialBlock, block_nonce: int) -> str:
    """ Computes block hash by solving a cryptographic puzzle
    :param initial_block: block with initial hash & nonce
    :param block_nonce: golden nonce
    :return: block hash
    """
    initial_block_hash = hash_initial_block(initial_block)
    return sha256((str(block_nonce) + initial_block_hash).encode()).hexdigest()


def hash_initial_block(initial_block: InitialBlock) -> str:
    """ Hashes block with initial hash & nonce
    :param initial_block: block with initial hash & nonce
    :return: hashed block
    """
    encoded_initial_block = json.dumps(initial_block, sort_keys=True).encode()
    return sha256(encoded_initial_block).hexdigest()


def update_initial_block(initial_block: InitialBlock,
                         new_block_hash: str,
                         new_block_nonce: int,
                         new_block_difficulty: float) -> Block:
    """ Updates block with new hash, nonce & difficulty
    :param initial_block: initial block
    :param new_block_hash: new block hash
    :param new_block_nonce: new block nonce
    :param new_block_difficulty: new block difficulty
    :return: block updated with new hash & nonce
    """
    new_block: Block = {k: v for k, v in initial_block.items()}
    new_block['hash'] = new_block_hash
    new_block['nonce'] = new_block_nonce
    new_block['difficulty'] = new_block_difficulty
    return new_block


def validate_block(prev_block_hash: str, new_block: Block) -> bool:
    """ Validates new mined block
    :param new_block: new mined block
    :return: new block validation status
    """
    # Prev & new blocks hashes validation
    if prev_block_hash != new_block['prev_hash']:
        return False

    # New block hash validation
    initial_block: InitialBlock = downgrade_block_to_initial(new_block)
    initial_block_target: str = compute_initial_block_target(new_block['bits'])
    initial_block_hash: str = compute_initial_block_hash(initial_block, new_block['nonce'])

    if new_block['hash'] != initial_block_hash or initial_block_target <= f'0x{initial_block_hash}':
        return False

    return True


def downgrade_block_to_initial(block: Block) -> InitialBlock:
    """ Strips block down to initial block
    :param block: block
    :return: initial block
    """
    return {k: v for k, v in block.items() if k != 'hash' and k != 'nonce' and k != 'difficulty'}
