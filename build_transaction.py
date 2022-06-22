from typing import TypedDict
from decimal import Decimal
from functools import reduce


# TODO: miner fees
# TODO: transactions choice
# Build transaction
class TransactionInput(TypedDict):
    sender: str
    amount: float


class TransactionOutput(TypedDict):
    receiver: str
    amount: float


class Transaction(TypedDict):
    inputs: list[TransactionInput]
    outputs: list[TransactionOutput]


def create_coinbase_transaction(sender: str, receiver: str, amount: float) -> Transaction:
    """ Creates a coinbase transaction with data
    :param sender: transaction sender
    :param receiver: transaction receiver
    :param amount: transaction amount
    :return: new transaction
    """
    return {'inputs': [{'sender': sender, 'amount': amount}],
            'outputs': [{'receiver': receiver, 'amount': amount}]
            }


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
