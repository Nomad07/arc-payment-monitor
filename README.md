# Arc Payment Monitor

A lightweight Python tool for monitoring USDC payments on the Arc network.

## Features

* Connect to the Arc network through RPC
* Validate Arc wallet addresses
* Display Arc chain ID
* Display the latest block number
* Display the current USDC balance
* Monitor incoming and outgoing USDC payments
* Show transaction details
* Calculate total received and total sent

## Requirements

* Python 3.10+
* `web3.py`

## Installation

Clone the repository:

```bash
git clone https://github.com/Nomad07/arc-payment-monitor.git
cd arc-payment-monitor
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the monitor:

```bash
python main.py
```

Enter an Arc wallet address when prompted.

The monitor displays the wallet balance and USDC payment activity on the Arc network.

## Network

The tool is currently configured for the Arc Testnet.

* Network: Arc Testnet
* Chain ID: 5042002
* USDC: `0x3600000000000000000000000000000000000000`

## Project Status

This project is under active development.

Planned improvements include:

* Real-time payment monitoring
* New payment notifications
* Improved transaction history
* Additional payment statistics

## License

MIT License
