import sys
import time

from web3 import Web3


RPC_URL = "https://rpc.testnet.arc.network"

TOKENS = {
    "USDC": {
        "address": "0x3600000000000000000000000000000000000000",
        "decimals": 6,
    },
    "EURC": {
        "address": "0x89B50855Aa3bE2F677cD6303Cec089B5F319D72a",
        "decimals": 6,
    },
    "cirBTC": {
        "address": "0xf0C4a4CE82A5746AbAAd9425360Ab04fbBA432BF",
        "decimals": 8,
    },
}


TRANSFER_TOPIC = Web3.keccak(
    text="Transfer(address,address,uint256)"
).hex()


web3 = Web3(Web3.HTTPProvider(RPC_URL))


BALANCE_ABI = [
    {
        "constant": True,
        "inputs": [
            {
                "name": "account",
                "type": "address",
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "",
                "type": "uint256",
            }
        ],
        "type": "function",
    }
]


def check_address(address):
    return Web3.is_address(address)


def decode_address(topic):
    return Web3.to_checksum_address(
        "0x" + topic.hex()[-40:]
    )


def get_token_by_address(contract_address):
    for name, token in TOKENS.items():
        if token["address"].lower() == contract_address.lower():
            return name, token

    return None, None


def get_token_balance(wallet_address, token_name):
    token = TOKENS[token_name]

    try:
        contract = web3.eth.contract(
            address=Web3.to_checksum_address(
                token["address"]
            ),
            abi=BALANCE_ABI,
        )

        raw_balance = contract.functions.balanceOf(
            wallet_address
        ).call()

        return raw_balance / (
            10 ** token["decimals"]
        )

    except Exception:
        return None


def get_balances(wallet_address):
    balances = {}

    for name in TOKENS:
        balances[name] = get_token_balance(
            wallet_address,
            name,
        )

    return balances


def decode_transfer(log, wallet_address):
    if len(log["topics"]) < 3:
        return None

    if log["topics"][0].hex() != TRANSFER_TOPIC:
        return None

    token_name, token = get_token_by_address(
        log["address"]
    )

    if token is None:
        return None

    from_address = decode_address(
        log["topics"][1]
    )

    to_address = decode_address(
        log["topics"][2]
    )

    wallet_lower = wallet_address.lower()

    if from_address.lower() == wallet_lower:
        direction = "OUT"

    elif to_address.lower() == wallet_lower:
        direction = "IN"

    else:
        return None

    amount_raw = int.from_bytes(
        log["data"],
        byteorder="big",
    )

    amount = amount_raw / (
        10 ** token["decimals"]
    )

    return {
        "token": token_name,
        "direction": direction,
        "amount": amount,
        "from": from_address,
        "to": to_address,
    }


def process_transaction(tx_hash, wallet_address):
    try:
        receipt = web3.eth.get_transaction_receipt(
            tx_hash
        )

    except Exception:
        return []

    payments = []

    for log in receipt.logs:
        payment = decode_transfer(
            log,
            wallet_address,
        )

        if payment:
            payment["tx"] = tx_hash
            payment["block"] = receipt.blockNumber
            payments.append(payment)

    return payments


def process_block(block_number, wallet_address):
    try:
        block = web3.eth.get_block(
            block_number,
            full_transactions=True,
        )

    except Exception:
        return []

    token_addresses = {
        token["address"].lower()
        for token in TOKENS.values()
    }

    payments = []

    for transaction in block.transactions:
        tx_to = transaction["to"]

        if not tx_to:
            continue

        if tx_to.lower() not in token_addresses:
            continue

        tx_hash = transaction["hash"].hex()

        detected = process_transaction(
            tx_hash,
            wallet_address,
        )

        payments.extend(detected)

    return payments


def print_payment(
    payment,
    wallet_address,
):
    print()
    print("=" * 50)
    print("NEW PAYMENT")
    print("=" * 50)
    print()

    if payment["direction"] == "IN":
        print(
            f"IN   +{payment['amount']:.8f} "
            f"{payment['token']}"
        )

    else:
        print(
            f"OUT  -{payment['amount']:.8f} "
            f"{payment['token']}"
        )

    print()
    print(f"From:  {payment['from']}")
    print(f"To:    {payment['to']}")
    print(f"Block: {payment['block']}")
    print(f"Tx:    {payment['tx']}")

    balance = get_token_balance(
        wallet_address,
        payment["token"],
    )

    if balance is not None:
        print()
        print(
            f"Balance: {balance:.8f} "
            f"{payment['token']}"
        )

    print()
    print("=" * 50)


def show_balances(wallet_address):
    print()
    print("Token Balances")
    print("--------------")

    balances = get_balances(wallet_address)

    for name in TOKENS:
        balance = balances[name]

        if balance is None:
            print(
                f"{name}: unable to read balance"
            )

        else:
            print(
                f"{name}: {balance:.8f}"
            )


def show_configured_tokens():
    print()
    print("Configured Tokens")
    print("-----------------")

    for name, token in TOKENS.items():
        print(
            f"{name}: {token['address']}"
        )


def watch(wallet_address):
    print()
    print("Watching for new payments...")
    print("Press Ctrl+C to stop.")
    print()

    last_block = web3.eth.block_number

    processed_transactions = set()

    while True:
        try:
            latest_block = web3.eth.block_number

            if latest_block > last_block:

                for block_number in range(
                    last_block + 1,
                    latest_block + 1,
                ):

                    payments = process_block(
                        block_number,
                        wallet_address,
                    )

                    for payment in payments:

                        tx_hash = payment["tx"]

                        if (
                            tx_hash
                            in processed_transactions
                        ):
                            continue

                        processed_transactions.add(
                            tx_hash
                        )

                        print_payment(
                            payment,
                            wallet_address,
                        )

                last_block = latest_block

            time.sleep(3)

        except KeyboardInterrupt:
            print()
            print("Monitor stopped.")
            break

        except Exception as error:
            print()
            print(
                f"Monitor error: {error}"
            )
            print(
                "Retrying in 5 seconds..."
            )
            time.sleep(5)


def main():
    print("Arc Payment Monitor")
    print("-------------------")

    address = input(
        "Enter Arc wallet address: "
    )

    if not check_address(address):
        print("Invalid wallet address")
        return

    address = Web3.to_checksum_address(
        address
    )

    print("Valid wallet address")

    if not web3.is_connected():
        print(
            "Could not connect to Arc RPC"
        )
        return

    print("Connected to Arc")

    chain_id = web3.eth.chain_id
    latest_block = web3.eth.block_number

    print(f"Network: Arc")
    print(f"Chain ID: {chain_id}")
    print(
        f"Latest block: {latest_block}"
    )

    show_balances(address)
    show_configured_tokens()

    if "--watch" in sys.argv:
        watch(address)

    else:
        print()
        print("Monitor ready.")
        print(
            "Run with --watch "
            "to monitor new payments."
        )


if __name__ == "__main__":
    main()