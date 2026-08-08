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

## How to Run

Run the application:

```bash
python main.py
```

Enter your Arc wallet address when prompted.

## Example

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
├── LICENSE
├── README.md
├── main.py
└── requirements.txt
```

## License

This project is licensed under the MIT License.



