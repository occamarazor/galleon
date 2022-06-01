import json
from hashlib import sha256
from typing import TypedDict, Final
from datetime import datetime
from flask import Flask, jsonify

TARGET_ZEROS: Final = '0000'


# Block dict
class Block(TypedDict):
    index: int
    timestamp: str
    nonce: int
    prev_hash: str


# Blockchain
class Blockchain:
    def __init__(self):
        # Create init hain
        self.chain = []
        # Create genesis block
        self.create_block(block_nonce=1, block_prev_hash='0')

    def create_block(self, block_nonce: int, block_prev_hash: str) -> dict:
        """Creates new block with data & appends it to the chain
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

        while nonce_is_valid is False:
            possible_hash: str = sha256(f'{new_block_nonce ** 2 - prev_block_nonce ** 2}'.encode()).hexdigest()

            if possible_hash[:4] == TARGET_ZEROS:
                nonce_is_valid = True
            else:
                new_block_nonce += 1

        return new_block_nonce

# Mining
