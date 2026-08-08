# Arc Wallet Checker

A simple Python tool for checking wallet information on the Arc network.

## Features

* Validate an Arc wallet address
* Connect to the Arc RPC
* Display the Arc chain ID
* Display the latest block number
* Check the native USDC balance
* Check the USDC token balance

## Requirements

* Python 3.12+
* web3.py

## Installation

Clone the repository:

```bash
git clone https://github.com/Nomad07/arc-wallet-checker.git
cd arc-wallet-checker
```

Install the required dependency:

```bash
pip install -r requirements.txt
```

## Usage

Run the wallet checker:

```bash
python main.py
```

Enter your Arc wallet address when prompted.

The application will validate the address, connect to the Arc network, and display the current wallet information.

## Example Output

```text
Arc Wallet Checker
------------------
Enter Arc wallet address: 0x...

Valid wallet address
Connected to Arc
Network: Arc
Chain ID: 5042002
Latest block: 55956868
Native USDC Balance: 41.796567066423713852
USDC Balance: 41.796567
```

## Project Structure

```text
arc-wallet-checker/
├── .gitignore
├── README.md
├── main.py
└── requirements.txt
```

## Network

The project connects to the Arc testnet through the official Arc RPC endpoint.

Chain ID:

```text
5042002
```

## License

This project is licensed under the MIT License.


