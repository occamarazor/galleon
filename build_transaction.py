from typing import TypedDict
from decimal import Decimal
from functools import reduce


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
    return {"inputs": [{"sender": sender, "amount": amount}],
            "outputs": [{"receiver": receiver, "amount": amount}]
            }


def validate_transaction(transaction: Transaction) -> bool:
    """ Validates transaction
    :param transaction: transaction
    :return: transaction validation status
    """
    try:
        transaction_inputs: float = float(sum(Decimal(f'{t_input["amount"]}') for t_input in transaction['inputs']))
        transaction_outputs: float = reduce(lambda x, y: float(Decimal(str(x)) + Decimal(str(y['amount']))),
                                            transaction['outputs'],
                                            0.0
                                            )
        return transaction_inputs == transaction_outputs
    except Exception as err:
        print(f'validate_transaction error: {repr(err)}')
        return False


def validate_mempool(mempool: list[Transaction]) -> bool:
    """ Validates mempool
    :param mempool: node mempool
    :return: mempool validation status
    """
    is_mempool_valid = True

    for transaction in mempool:
        is_transaction_valid = validate_transaction(transaction)
        is_mempool_valid = is_transaction_valid

    return is_mempool_valid
