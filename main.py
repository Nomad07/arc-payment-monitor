from web3 import Web3

RPC_URL = "https://rpc.testnet.arc.network"

web3 = Web3(Web3.HTTPProvider(RPC_URL))


def check_address(address):
    return Web3.is_address(address)


def get_balance(address):
    balance = web3.eth.get_balance(address)
    return web3.from_wei(balance, "ether")


def main():
    print("Arc Wallet Checker")
    print("------------------")

    address = input("Enter Arc wallet address: ")

    if not check_address(address):
        print("Invalid wallet address")
        return

    print("Valid wallet address")

    if not web3.is_connected():
        print("Could not connect to Arc RPC")
        return

    print("Connected to Arc")

    chain_id = web3.eth.chain_id
    print(f"Chain ID: {chain_id}")

    balance = get_balance(address)

    print(f"Balance: {balance} ETH")


if __name__ == "__main__":
    main()
