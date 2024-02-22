## blockchain_interface.py
import logging
from typing import Optional
from web3 import Web3, exceptions
from web3.contract import Contract
from pyramid_scheme.utils import validate_ethereum_address, convert_to_ether

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from web3 import Web3, exceptions
except ImportError:
    logger.error("Failed to import web3. Make sure the web3 package is installed.")
    raise

def handle_transaction_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions.BadFunctionCallOutput:
            logger.error("Function call failed")
            return False
        except exceptions.TransactionFailed as e:
            logger.error(f"Transaction failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
    return wrapper

class BlockchainInterface:
    def __init__(self, provider_url: str = "http://127.0.0.1:8545") -> None:
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        self.contract: Optional[Contract] = None

    def deploy_contract(self, contract_abi: str, contract_bytecode: str, deployer_address: str, deployer_private_key: str) -> str:
        if not self.web3.isConnected():
            raise ConnectionError("Web3 is not connected to any Ethereum node")
        if not validate_ethereum_address(deployer_address):
            raise ValueError("Invalid Ethereum address")

        self.web3.eth.defaultAccount = deployer_address
        ContractFactory = self.web3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
        transaction = ContractFactory.constructor().buildTransaction({
            'from': deployer_address,
            'nonce': self.web3.eth.getTransactionCount(deployer_address),
            'gas': 2000000,
            'gasPrice': self.web3.toWei('50', 'gwei')
        })

        signed_txn = self.web3.eth.account.signTransaction(transaction, private_key=deployer_private_key)
        tx_hash = self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)

        self.contract = self.web3.eth.contract(address=tx_receipt.contractAddress, abi=contract_abi)
        return tx_receipt.contractAddress

    def execute_transaction(self, function_call, **transaction_parameters):
        tx_hash = function_call.transact(transaction_parameters)
        self.web3.eth.waitForTransactionReceipt(tx_hash)
        return True

    @handle_transaction_errors
    def join_scheme(self, address: str, amount: int) -> bool:
        if not self.contract:
            raise RuntimeError("Contract is not deployed")
        if not validate_ethereum_address(address):
            raise ValueError("Invalid Ethereum address")

        return self.execute_transaction(self.contract.functions.joinScheme(), from=address, value=self.web3.toWei(amount, 'ether'), gas=1000000)

    @handle_transaction_errors
    def withdraw_earnings(self, address: str) -> bool:
        if not self.contract:
            raise RuntimeError("Contract is not deployed")
        if not validate_ethereum_address(address):
            raise ValueError("Invalid Ethereum address")

        return self.execute_transaction(self.contract.functions.withdrawEarnings(), from=address, gas=1000000)

    @handle_transaction_errors
    def view_earnings(self, address: str) -> int:
        if not self.contract:
            raise RuntimeError("Contract is not deployed")
        if not validate_ethereum_address(address):
            raise ValueError("Invalid Ethereum address")

        try:
            earnings = self.contract.functions.viewEarnings(address).call()
            return convert_to_ether(earnings)
        except exceptions.BadFunctionCallOutput:
            logger.error("Function call failed")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return 0

    @handle_transaction_errors
    def refer_friend(self, inviter: str, invitee: str) -> bool:
        if not self.contract:
            raise RuntimeError("Contract is not deployed")
        if not validate_ethereum_address(inviter) or not validate_ethereum_address(invitee):
            raise ValueError("Invalid Ethereum address")

        return self.execute_transaction(self.contract.functions.referFriend(inviter, invitee), from=inviter, gas=1000000)
