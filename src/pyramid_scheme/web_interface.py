## web_interface.py
import logging
from typing import Any

import utils
from flask import Flask, jsonify, request

from pyramid_scheme.blockchain_interface import BlockchainInterface


class WebInterface:
    def __init__(self, blockchain_interface: BlockchainInterface) -> None:
        self.app = Flask(__name__)
        self.blockchain_interface = blockchain_interface

    def init_app(self) -> None:
        self._setup_routes()

    def _setup_routes(self) -> None:
        @self.app.route("/deploy_contract", methods=["POST"])
        def deploy_contract() -> Any:
            try:
                result = self.blockchain_interface.deploy_contract()
                return jsonify({"success": True, "contract_address": result}), 200
            except Exception as e:
                logging.error(f"Failed to deploy contract: {e}")
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/join_scheme", methods=["POST"])
        def join_scheme() -> Any:
            data = request.json
            address = data.get("address")
            try:
                amount = float(data.get("amount"))
            except ValueError:
                return jsonify({"success": False, "error": "Invalid amount"}), 400

            if not utils.validate_ethereum_address(address):
                return (
                    jsonify({"success": False, "error": "Invalid Ethereum address"}),
                    400,
                )

            try:
                result = self.blockchain_interface.join_scheme(address, amount)
                return jsonify({"success": result}), 200
            except Exception as e:
                logging.error(f"Failed to join scheme: {e}")
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/withdraw_earnings", methods=["POST"])
        def withdraw_earnings() -> Any:
            data = request.json
            address = data.get("address")
            if not utils.validate_ethereum_address(address):
                return (
                    jsonify({"success": False, "error": "Invalid Ethereum address"}),
                    400,
                )

            try:
                result = self.blockchain_interface.withdraw_earnings(address)
                return jsonify({"success": result}), 200
            except Exception as e:
                logging.error(f"Failed to withdraw earnings: {e}")
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/view_earnings", methods=["GET"])
        def view_earnings() -> Any:
            address = request.args.get("address")
            if not utils.validate_ethereum_address(address):
                return (
                    jsonify({"success": False, "error": "Invalid Ethereum address"}),
                    400,
                )

            try:
                earnings = self.blockchain_interface.view_earnings(address)
                return jsonify({"success": True, "earnings": earnings}), 200
            except Exception as e:
                logging.error(f"Failed to view earnings: {e}")
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/refer_friend", methods=["POST"])
        def refer_friend() -> Any:
            data = request.json
            inviter = data.get("inviter")
            invitee = data.get("invitee")
            if not utils.validate_ethereum_address(
                inviter
            ) or not utils.validate_ethereum_address(invitee):
                return (
                    jsonify({"success": False, "error": "Invalid Ethereum address"}),
                    400,
                )

            try:
                result = self.blockchain_interface.refer_friend(inviter, invitee)
                return jsonify({"success": result}), 200
            except Exception as e:
                logging.error(f"Failed to refer friend: {e}")
                return jsonify({"success": False, "error": str(e)}), 500

    def run(self) -> None:
        self.app.run(host="0.0.0.0", port=5000, debug=True)
