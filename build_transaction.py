from typing import TypedDict
from decimal import Decimal
from functools import reduce
from uuid import uuid4


# TODO: miner fees
# TODO: transactions choice
# TODO: transactions hash
# Build transaction
class TransactionInput(TypedDict):
    sender: str
    amount: float


class TransactionOutput(TypedDict):
    receiver: str
    amount: float


class InitialTransaction(TypedDict):
    inputs: list[TransactionInput]
    outputs: list[TransactionOutput]


class Transaction(InitialTransaction):
    id: str


def create_coinbase_transaction(sender: str, receiver: str, amount: float) -> Transaction:
    """ Creates a coinbase transaction with data
    :param sender: transaction sender
    :param receiver: transaction receiver
    :param amount: transaction amount
    :return: new coinbase transaction
    """
    return {'id': uuid4().hex,
            'inputs': [{'sender': sender, 'amount': amount}],
            'outputs': [{'receiver': receiver, 'amount': amount}]
            }


def create_transaction(initial_transaction: InitialTransaction) -> Transaction:
    """ Creates a new transaction with id
    :param initial_transaction: coinbase transaction
    :return: new transaction with id
    """
    new_transaction: Transaction = {k: v for k, v in initial_transaction.items()}
    if 'id' not in new_transaction:
        new_transaction['id'] = uuid4().hex
    return new_transaction


def validate_transaction(new_transaction: Transaction) -> bool:
    """ Validates transaction
    :param new_transaction: new transaction
    :return: new transaction validation status
    """
    try:
        transaction_inputs: float = float(sum(Decimal(f'{t_input["amount"]}') for t_input in new_transaction['inputs']))
        transaction_outputs: float = reduce(lambda x, y: float(Decimal(str(x)) + Decimal(str(y['amount']))),
                                            new_transaction['outputs'],
                                            0.0
                                            )
        return transaction_inputs == transaction_outputs
    except Exception as err:
        print(f'validate_transaction error: {repr(err)}')
        return False
