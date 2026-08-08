from web3 import Web3

RPC_URL = "https://rpc.testnet.arc.network"
USDC_ADDRESS = "0x3600000000000000000000000000000000000000"

web3 = Web3(Web3.HTTPProvider(RPC_URL))

USDC_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
]


def check_address(address):
    return Web3.is_address(address)


def get_native_usdc_balance(address):
    balance = web3.eth.get_balance(address)
    return web3.from_wei(balance, "ether")


def get_usdc_balance(address):
    contract = web3.eth.contract(
        address=Web3.to_checksum_address(USDC_ADDRESS),
        abi=USDC_ABI,
    )

    raw_balance = contract.functions.balanceOf(address).call()
    decimals = contract.functions.decimals().call()

    return raw_balance / (10 ** decimals)


def main():
    print("Arc Wallet Checker")
    print("------------------")

    address = input("Enter Arc wallet address: ")

    if not check_address(address):
        print("Invalid wallet address")
        return

    address = Web3.to_checksum_address(address)

    print("Valid wallet address")

    if not web3.is_connected():
        print("Could not connect to Arc RPC")
        return

    print("Connected to Arc")

    chain_id = web3.eth.chain_id
    print("Network: Arc")
    print(f"Chain ID: {chain_id}")

    block_number = web3.eth.block_number
    print(f"Latest block: {block_number}")

    native_balance = get_native_usdc_balance(address)
    print(f"Native USDC Balance: {native_balance}")

    usdc_balance = get_usdc_balance(address)
    print(f"USDC Balance: {usdc_balance}")


if __name__ == "__main__":
    main()
