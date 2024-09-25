from typing import List, Dict

from tronpy import Tron
from tronpy import keys
from tronpy.contract import Contract
from tronpy.exceptions import ApiError, AddressNotFound


class TronProxyClient(Tron):
    def get_contract_with_custom_abi(self, addr: str, abi: List[Dict]) -> Contract:
        """Get a contract object."""
        addr = keys.to_base58check_address(addr)
        info = self.provider.make_request("wallet/getcontract", {"value": addr, "visible": True})

        try:
            self._handle_api_error(info)
        except ApiError:
            # your java's null pointer exception sucks
            raise AddressNotFound("contract address not found")

        cntr = Contract(
            addr=addr,
            bytecode=info.get("bytecode", ''),
            name=info.get("name", ""),
            abi=abi,
            origin_energy_limit=info.get("origin_energy_limit", 0),
            user_resource_percent=info.get("consume_user_resource_percent", 100),
            client=self,
        )
        return cntr
