# Arc Wallet Checker

A lightweight Python utility for checking wallet information on the **Arc network**.

[![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python\&logoColor=white)](https://www.python.org/)
[![Network](https://img.shields.io/badge/Network-Arc-black)](https://arc.network/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## Overview

**Arc Wallet Checker** is a simple command-line tool built with Python and `web3.py`.

It connects directly to the Arc RPC and displays basic information about an Arc wallet, including its network status, chain ID, latest block, and USDC balance.

## Features

* ✅ Validate an Arc wallet address
* 🔗 Connect to the Arc RPC
* 🌐 Display the Arc network
* 🔢 Display the Arc chain ID
* 📦 Display the latest block number
* 💰 Check the USDC balance
* ⚡ Lightweight command-line interface

## Requirements

* Python 3.12+
* `web3.py`

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
Latest block: 56165330
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

This project is licensed under the [MIT License](LICENSE).




