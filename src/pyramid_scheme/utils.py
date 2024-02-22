## utils.py
from typing import Union

from web3 import Web3


class Utils:
    @staticmethod
    def validate_ethereum_address(address: str) -> bool:
        """
        Validates an Ethereum address.

        Parameters:
        address (str): The Ethereum address to validate.

        Returns:
        bool: True if the address is valid, False otherwise.
        """
        if not isinstance(address, str):
            return False
        return Web3.isAddress(address)

    @staticmethod
    def convert_to_ether(wei: int) -> Union[float, None]:
        """
        Converts Wei to Ether.

        Parameters:
        wei (int): The amount in Wei to convert.

        Returns:
        float: The equivalent amount in Ether.
        """
        if not isinstance(wei, int):
            return None
        return Web3.fromWei(wei, "ether")
