# Arc Payment Monitor

Real-time token payment monitoring for the Arc network.

The monitor tracks incoming and outgoing transfers for USDC, EURC and cirBTC, displays token balances, and watches the Arc blockchain for new payments in real time.

## Features

- Connect to the Arc network through RPC
- Validate Arc wallet addresses
- Display Arc chain ID
- Display the latest block number
- Display balances for USDC, EURC and cirBTC
- Monitor incoming and outgoing token payments
- Detect new payments in real time
- Show sender and recipient addresses
- Show block numbers
- Show transaction hashes
- Display updated token balances after payments
- Track session payment statistics
- Count incoming and outgoing transfers
- Calculate total received and total sent for each token
- Browser-based monitoring interface

## Supported Tokens

| Token | Decimals | Contract |
| --- | ---: | --- |
| USDC | 6 | `0x3600000000000000000000000000000000000000` |
| EURC | 6 | `0x89B50855Aa3bE2F677cD6303Cec089B5F319D72a` |
| cirBTC | 8 | `0xf0C4a4CE82A5746AbAAd9425360Ab04fbBA432BF` |

## Requirements

- Python 3.10+
- `web3.py`
- `Flask` for the web interface

## Installation

Clone the repository:

    git clone https://github.com/Nomad07/arc-payment-monitor.git
    cd arc-payment-monitor

Install dependencies:

    pip install -r requirements.txt

## Usage

### Command Line Monitor

Run the monitor:

    python main.py

Enter an Arc wallet address when prompted.

The monitor displays:

- Arc network information
- Current token balances
- Configured token contracts

### Real-Time Monitoring

To monitor new payments in real time, run:

    python main.py --watch

The monitor will wait for new token transfers and display them as they are detected.

Example:

    Watching for new payments...
    Press Ctrl+C to stop.

    ==================================================
    NEW PAYMENT
    ==================================================

    IN   +20.00000000 USDC

    From:  0x...
    To:    0x...
    Block: 56615623
    Tx:    0x...

    Balance: 141.79656700 USDC

The same monitoring process works for USDC, EURC and cirBTC.

Press `Ctrl+C` to stop the monitor.

## Web Interface

Arc Payment Monitor also includes a browser-based interface for monitoring payments.

Start the web interface:

    python web_gui.py

The interface runs on port `5000`.

The web interface provides:

- Arc network connection status
- Wallet connection
- Live token balances
- Real-time payment detection
- Incoming and outgoing payment information
- Sender and recipient addresses
- Block numbers
- Transaction hashes
- Session payment statistics

The interface automatically refreshes the displayed data while monitoring is active.

Example:

    Arc Payment Monitor

    Connected to Arc | Chain ID: 5042002

    Token Balances

    USDC
    201.79656700

    EURC
    224.00000000

    cirBTC
    0.00110000

    Live Payments

    IN +20.00000000 EURC

    From: 0x...
    To:   0x...
    Block: 56631945
    Tx: 0x...

## Payment Statistics

During a monitoring session, the tool tracks payment activity for each supported token.

Example:

    Session Statistics

    USDC
    Incoming:  1
    Outgoing:  0
    Received:  20.00000000
    Sent:      0.00000000

    EURC
    Incoming:  1
    Outgoing:  0
    Received:  20.00000000
    Sent:      0.00000000

    cirBTC
    Incoming:  1
    Outgoing:  0
    Received:  0.00010000
    Sent:      0.00000000

The statistics are updated while the monitoring session is active.

## Network

The tool is currently configured for the Arc Testnet.

- Network: Arc Testnet
- Chain ID: `5042002`
- RPC: `https://rpc.testnet.arc.network`

## Project Status

Arc Payment Monitor is an active project focused on on-chain payment monitoring for the Arc network.

The current version supports:

- USDC monitoring
- EURC monitoring
- cirBTC monitoring
- Real-time payment detection
- Incoming and outgoing transfer detection
- Token balance tracking
- Transaction details
- Session payment statistics
- Browser-based monitoring interface

The project is currently focused on reliable payment detection and a straightforward monitoring experience.

More monitoring and analytics features may be added as the project develops.

## License

MIT License
