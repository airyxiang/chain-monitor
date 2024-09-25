import json

from chain_monitor.web3.contract.contract_factory import (
    CommonControllerContractFunctionsMixin
)
from chain_monitor.web3.contract.web3_wrapper import bsc_web3 as web3


class ControllerContract(CommonControllerContractFunctionsMixin):
    def __init__(self, address):
        if ControllerContract.abi is None:
            with open("./chain_monitor/web3/contract/abi/bsc_abi/controller_abi.json", "r") as abi:
                ControllerContract.abi = json.load(abi)
        self.address = web3.to_checksum_address(address)
        self.instance = web3.create_contract_instance(self.address, ControllerContract.abi)

    def get_set_can_burn_call_data(self, to_address, value):
        return self.instance.encodeABI(fn_name="setCanBurn", args=[to_address, value])


ControllerContract.abi = None
