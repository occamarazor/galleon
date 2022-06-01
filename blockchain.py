import hashlib
import json
from typing import TypedDict
from datetime import datetime

from flask import Flask, jsonify


# Block dict
class Block(TypedDict):
    index: int
    timestamp: str
    proof: int
    prev_hash: str


# Blockchain
class Blockchain:
    def __init__(self):
        # Create init hain
        self.chain = []
        # Create genesis block
        self.create_block(proof=1, prev_hash='0')

    def create_block(self, proof: int, prev_hash: str) -> dict:
        """Creates new block with data & appends it to the chain
        :param proof: block proof
        :param prev_hash: previous block hash
        :return: new created block
        """
        block: Block = {'index': len(self.chain) + 1,
                        'timestamp': f'{datetime.now()}',
                        'proof': proof,
                        'prev_hash': prev_hash
                        }
        self.chain.append(block)
        return block

# Mining
