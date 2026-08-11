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

TEST_TRANSACTIONS = [
    "0x031103c6bac8a20ec5497216f9f804281b4da70c3af3b6a86b5e303245ae5670",
    "0xcc3f94da36a01aa363ca31e00dbb7553078da3665b472456336381a23a1c0584",
    "0x05dc3dcc0ea559fe09efab8f7abb43c21196c1a7a49a4536c3a854add42fd45c",
]

web3 = Web3(Web3.HTTPProvider(RPC_URL))


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


def decode_transfer(log, wallet_address):
    if len(log["topics"]) < 3:
        return None

    if log["topics"][0].hex() != TRANSFER_TOPIC:
        return None

    token_name, token = get_token_by_address(log["address"])

    if token is None:
        return None

    from_address = decode_address(log["topics"][1])
    to_address = decode_address(log["topics"][2])

    wallet_address = wallet_address.lower()

    if from_address.lower() == wallet_address:
        direction = "OUT"
    elif to_address.lower() == wallet_address:
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


def check_transaction(tx_hash, wallet_address):
    receipt = web3.eth.get_transaction_receipt(tx_hash)

    results = []

    for log in receipt.logs:
        transfer = decode_transfer(
            log,
            wallet_address,
        )

        if transfer:
            transfer["tx"] = tx_hash
            transfer["block"] = receipt.blockNumber
            results.append(transfer)

    return results


def main():
    print("Arc Payment Monitor")
    print("-------------------")

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

    print(f"Network: Arc")
    print(f"Chain ID: {web3.eth.chain_id}")
    print(f"Latest block: {web3.eth.block_number}")

    print()
    print("Token Balances")
    print("-------------")

    balance_abi = [
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

    for name, token in TOKENS.items():
        try:
            contract = web3.eth.contract(
                address=Web3.to_checksum_address(
                    token["address"]
                ),
                abi=balance_abi,
            )

            raw_balance = contract.functions.balanceOf(
                address
            ).call()

            balance = raw_balance / (
                10 ** token["decimals"]
            )

            print(f"{name}: {balance:.8f}")

        except Exception as error:
            print(f"{name}: unable to read balance")
            print(error)

    print()
    print("Testing Payment Detection")
    print("-------------------------")

    payments = []

    for tx_hash in TEST_TRANSACTIONS:
        try:
            detected = check_transaction(
                tx_hash,
                address,
            )

            payments.extend(detected)

        except Exception as error:
            print()
            print(f"Could not read transaction:")
            print(tx_hash)
            print(error)

    if not payments:
        print("No matching payments found.")
    else:
        for payment in payments:
            print()

            if payment["direction"] == "IN":
                print(
                    f"IN   +{payment['amount']:.8f} "
                    f"{payment['token']}"
                )
                print(f"From: {payment['from']}")
                print(f"To:   {payment['to']}")

            else:
                print(
                    f"OUT  -{payment['amount']:.8f} "
                    f"{payment['token']}"
                )
                print(f"From: {payment['from']}")
                print(f"To:   {payment['to']}")

            print(f"Block: {payment['block']}")
            print(f"Tx:    {payment['tx']}")

    print()
    print("-------------------------")
    print("Payment detection test complete.")


if __name__ == "__main__":
    main()