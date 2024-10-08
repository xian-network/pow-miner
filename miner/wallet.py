from config import PRIVATE_KEY, RPC_NODE_URL, CONTRACT_NAME
from xian_py.wallet import Wallet
from xian_py.xian import Xian

wallet = Wallet(PRIVATE_KEY)
public_key = wallet.public_key

print(f"public_key: {public_key}")

xian = Xian(RPC_NODE_URL, wallet=wallet)


def submit_block(block):
    res = xian.send_tx(
        contract=CONTRACT_NAME,
        function="submit_it",
        kwargs={
            "key": public_key,
            "extra_data": block["extra_data"],
            "solution": block["solution"],
            "solution_height": block["height"],
        },
    )
    return res
