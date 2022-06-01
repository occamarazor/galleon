import json
from hashlib import sha256
from typing import TypedDict, Final
from datetime import datetime
from flask import Flask, jsonify

TARGET_ZEROS: Final = '0000'

# Block annotation
class Block(TypedDict):
    index: int
    timestamp: str
    nonce: int
    prev_hash: str


# Blockchain
class Blockchain:
    def __init__(self):
        # Create init hain
        self.chain: list[Block] = []
        # Create genesis block
        self.create_block(block_nonce=1, block_prev_hash='0')

    def calc_block_hash(self, block_nonce: int, prev_block_nonce: int) -> str:
        return sha256(f'{block_nonce ** 2 - prev_block_nonce ** 2}'.encode()).hexdigest()

    def create_block(self, block_nonce: int, block_prev_hash: str) -> Block:
        """Creates a new block with data & appends it to the chain
        :param block_nonce: block nonce
        :param block_prev_hash: previous block hash
        :return: new created block
        """
        new_block: Block = {'index': len(self.chain) + 1,
                            'timestamp': f'{datetime.now()}',
                            'nonce': block_nonce,
                            'prev_hash': block_prev_hash
                            }
        self.chain.append(new_block)
        return new_block

    def get_prev_block(self):
        return self.chain[-1]

    def proof_of_work(self, prev_block_nonce: int) -> int:
        """ Solves the cryptographic puzzle
        :param prev_block_nonce: previous block nonce
        :return: new block nonce
        """
        new_block_nonce: int = 1
        nonce_is_valid: bool = False

        # Compute hashes until golden nonce found
        while nonce_is_valid is False:
            possible_hash: str = self.calc_block_hash(new_block_nonce, prev_block_nonce)

            if possible_hash[:4] == TARGET_ZEROS:
                nonce_is_valid = True
            else:
                new_block_nonce += 1

        return new_block_nonce

    def hash_block(self, block: Block) -> str:
        """ Computes entire block hash
        :param block: block
        :return: encoded block hash
        """
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain: list[Block]) -> bool:
        """ Validates the entire blockchain
        :param chain: blockchain
        :return: boolean validation result
        """
        block_index: int = 1

        # Validate each block
        while block_index < len(chain):
            # Prev & current blocks hashes validation
            prev_block: Block = chain[block_index - 1]
            current_block: Block = chain[block_index]

            if self.hash_block(prev_block) != current_block['prev_hash']:
                return False

            # Current block hash validation
            prev_block_nonce = prev_block['nonce']
            current_block_nonce = current_block['nonce']
            current_block_hash: str = self.calc_block_hash(current_block_nonce, prev_block_nonce)

            if current_block_hash[:4] != TARGET_ZEROS:
                return False

            block_index += 1
            return True

# Mining
