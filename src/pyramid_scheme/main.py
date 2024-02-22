import logging

from flask import Flask
from web3 import HTTPProvider, Web3
from web_interface import WebInterface

from pyramid_scheme.blockchain_interface import BlockchainInterface

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Main:
    """
    Main class to initialize and run the Flask application and manage blockchain interactions.
    """

    def __init__(self):
        """
        Initializes the Flask app, Web3 instance, and interfaces for web and blockchain interactions.
        """
        self.app = Flask(__name__)
        try:
            self.web3 = Web3(HTTPProvider("http://127.0.0.1:8545"))
        except Exception as e:
            logging.error(f"Failed to connect to Ethereum node: {e}")
            raise

        self.web_interface = WebInterface(self.app)
        self.blockchain_interface = BlockchainInterface(self.web3)

    def run(self) -> None:
        """
        Initializes the web interface and starts the Flask application.
        """
        self.web_interface.init_app()
        try:
            self.app.run(host="0.0.0.0", port=5000)
        except Exception as e:
            logging.error(f"Failed to start Flask app: {e}")
            raise


if __name__ == "__main__":
    try:
        main = Main()
        main.run()
    except Exception as e:
        logging.error(f"Application failed to start: {e}")
