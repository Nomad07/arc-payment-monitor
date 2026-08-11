from web3 import Web3

RPC_URL = "https://rpc.testnet.arc.network"

TX_HASH = "0x031103c6bac8a20ec5497216f9f804281b4da70c3af3b6a86b5e303245ae5670"

web3 = Web3(Web3.HTTPProvider(RPC_URL))

print("Connected:", web3.is_connected())

receipt = web3.eth.get_transaction_receipt(TX_HASH)

print("Block:", receipt.blockNumber)
print("Status:", receipt.status)
print("Logs:", len(receipt.logs))

for i, log in enumerate(receipt.logs):
    print()
    print("LOG", i)
    print("Address:", log["address"])
    print("Topics:")

    for topic in log["topics"]:
        print(" ", topic.hex())

    print("Data:", log["data"].hex())
