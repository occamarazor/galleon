from typing import TypedDict


# Build transaction
class Transaction(TypedDict):
    sender: str
    receiver: str
    amount: float


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
