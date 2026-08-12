from flask import Flask, request, jsonify, render_template_string
from web3 import Web3
import threading
import time


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


TRANSFER_TOPIC = Web3.keccak(
    text="Transfer(address,address,uint256)"
).hex().lower()


web3 = Web3(
    Web3.HTTPProvider(RPC_URL)
)

app = Flask(__name__)


wallet_address = None
running = False
last_block = None


payments = []


statistics = {
    "USDC": {
        "incoming": 0,
        "outgoing": 0,
        "received": 0.0,
        "sent": 0.0,
    },
    "EURC": {
        "incoming": 0,
        "outgoing": 0,
        "received": 0.0,
        "sent": 0.0,
    },
    "cirBTC": {
        "incoming": 0,
        "outgoing": 0,
        "received": 0.0,
        "sent": 0.0,
    },
}


def get_balances():
    if not wallet_address:
        return {
            "USDC": 0,
            "EURC": 0,
            "cirBTC": 0,
        }

    balances = {}

    for name, token in TOKENS.items():

        try:

            contract = web3.eth.contract(
                address=Web3.to_checksum_address(
                    token["address"]
                ),
                abi=BALANCE_ABI,
            )

            raw_balance = (
                contract.functions.balanceOf(
                    wallet_address
                ).call()
            )

            balances[name] = (
                raw_balance
                / (10 ** token["decimals"])
            )

        except Exception as error:

            print(
                f"Balance error for {name}: "
                f"{error}"
            )

            balances[name] = None

    return balances


def reset_statistics():

    global payments

    payments = []

    for token_name in statistics:

        statistics[token_name] = {
            "incoming": 0,
            "outgoing": 0,
            "received": 0.0,
            "sent": 0.0,
        }


def decode_address(topic):

    topic_hex = topic.hex()

    return Web3.to_checksum_address(
        "0x" + topic_hex[-40:]
    )


def get_token_by_address(address):

    for name, token in TOKENS.items():

        if (
            address.lower()
            == token["address"].lower()
        ):
            return name, token

    return None, None


def process_log(log):

    if not wallet_address:
        return

    topics = log["topics"]

    if len(topics) < 3:
        return

    event_topic = topics[0].hex().lower()

    if event_topic != TRANSFER_TOPIC:
        return

    token_name, token = get_token_by_address(
        log["address"]
    )

    if token is None:
        return

    try:

        from_address = decode_address(
            topics[1]
        )

        to_address = decode_address(
            topics[2]
        )

    except Exception as error:

        print(
            f"Address decode error: {error}"
        )

        return

    wallet_lower = (
        wallet_address.lower()
    )

    if to_address.lower() == wallet_lower:

        direction = "IN"

    elif from_address.lower() == wallet_lower:

        direction = "OUT"

    else:

        return

    data_hex = log["data"].hex()

    amount_raw = int(
        data_hex,
        16
    )

    amount = (
        amount_raw
        / (10 ** token["decimals"])
    )

    block_number = log["blockNumber"]

    tx_hash = log[
        "transactionHash"
    ].hex()

    for payment in payments:

        if payment["tx"] == tx_hash:
            return

    payment = {
        "direction": direction,
        "token": token_name,
        "amount": amount,
        "from": from_address,
        "to": to_address,
        "block": block_number,
        "tx": tx_hash,
    }

    payments.insert(
        0,
        payment
    )

    if len(payments) > 50:
        payments.pop()

    if direction == "IN":

        statistics[token_name][
            "incoming"
        ] += 1

        statistics[token_name][
            "received"
        ] += amount

    else:

        statistics[token_name][
            "outgoing"
        ] += 1

        statistics[token_name][
            "sent"
        ] += amount

    print()
    print(
        "========================================"
    )

    print(
        "NEW PAYMENT DETECTED"
    )

    print(
        f"{direction} "
        f"+{amount:.8f} "
        f"{token_name}"
    )

    print(
        f"From:  {from_address}"
    )

    print(
        f"To:    {to_address}"
    )

    print(
        f"Block: {block_number}"
    )

    print(
        f"Tx:    {tx_hash}"
    )

    print(
        "========================================"
    )


def check_logs(
    from_block,
    to_block
):

    if from_block > to_block:
        return

    token_addresses = [
        Web3.to_checksum_address(
            token["address"]
        )
        for token in TOKENS.values()
    ]

    try:

        logs = web3.eth.get_logs(
            {
                "fromBlock": from_block,
                "toBlock": to_block,
                "address": token_addresses,
                "topics": [
                    TRANSFER_TOPIC
                ],
            }
        )

        print(
            f"Checking blocks "
            f"{from_block}-{to_block}: "
            f"{len(logs)} Transfer logs"
        )

        for log in logs:

            process_log(log)

    except Exception as error:

        print(
            f"Error reading Transfer logs: "
            f"{error}"
        )


def monitor():

    global last_block

    print(
        "Monitor thread started"
    )

    while running:

        try:

            current_block = (
                web3.eth.block_number
            )

            if last_block is None:

                last_block = (
                    current_block
                )

            if current_block > last_block:

                from_block = (
                    last_block + 1
                )

                to_block = (
                    current_block
                )

                check_logs(
                    from_block,
                    to_block
                )

                last_block = (
                    current_block
                )

        except Exception as error:

            print(
                f"Monitor error: {error}"
            )

        time.sleep(3)

    print(
        "Monitor thread stopped"
    )


HTML = """
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>Arc Payment Monitor</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #0b1020;
    color: #f1f5f9;
    font-family: Arial, sans-serif;
}

.container {
    max-width: 1100px;
    margin: auto;
    padding: 30px 20px;
}

h1 {
    margin-bottom: 5px;
}

.subtitle {
    color: #94a3b8;
    margin-bottom: 25px;
}

.panel {
    background: #111827;
    border: 1px solid #263244;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
}

.status {
    display: inline-block;
    padding: 7px 12px;
    border-radius: 20px;
    background: #172033;
    color: #94a3b8;
    margin-bottom: 10px;
}

.connected {
    color: #4ade80;
}

input {
    width: 100%;
    padding: 12px;
    margin-top: 10px;
    border-radius: 8px;
    border: 1px solid #334155;
    background: #0f172a;
    color: white;
}

button {
    margin-top: 12px;
    margin-right: 8px;
    padding: 11px 18px;
    border: 0;
    border-radius: 8px;
    background: #2563eb;
    color: white;
    cursor: pointer;
    font-weight: bold;
}

button:hover {
    background: #1d4ed8;
}

.balances {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
}

.balance {
    background: #0f172a;
    border: 1px solid #263244;
    border-radius: 10px;
    padding: 20px;
}

.token {
    color: #94a3b8;
}

.amount {
    margin-top: 8px;
    font-size: 24px;
    font-weight: bold;
}

.payment {
    border-top: 1px solid #263244;
    padding: 15px 0;
}

.payment:first-child {
    border-top: 0;
}

.incoming {
    color: #4ade80;
}

.outgoing {
    color: #f87171;
}

.details {
    color: #94a3b8;
    font-size: 13px;
    line-height: 1.7;
    margin-top: 6px;
    word-break: break-all;
}

.stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
}

.stat {
    background: #0f172a;
    border-radius: 10px;
    padding: 18px;
    border: 1px solid #263244;
}

.stat-line {
    color: #94a3b8;
    margin: 7px 0;
}

@media (max-width: 700px) {

    .balances,
    .stats {
        grid-template-columns: 1fr;
    }

}

</style>

</head>

<body>

<div class="container">

<h1>
Arc Payment Monitor
</h1>

<div class="subtitle">
Real-time token payment monitoring on Arc Testnet
</div>

<div class="panel">

<div
    id="status"
    class="status"
>
Not connected
</div>

<input
    id="wallet"
    placeholder="Enter Arc wallet address"
>

<button onclick="connectWallet()">
Connect Wallet
</button>

<button onclick="toggleMonitor()">
<span id="monitorButton">
Start Monitoring
</span>
</button>

</div>

<div class="panel">

<h2>
Token Balances
</h2>

<div class="balances">

<div class="balance">

<div class="token">
USDC
</div>

<div
    id="usdc"
    class="amount"
>
0.00000000
</div>

</div>

<div class="balance">

<div class="token">
EURC
</div>

<div
    id="eurc"
    class="amount"
>
0.00000000
</div>

</div>

<div class="balance">

<div class="token">
cirBTC
</div>

<div
    id="cirbtc"
    class="amount"
>
0.00000000
</div>

</div>

</div>

</div>

<div class="panel">

<h2>
Live Payments
</h2>

<div id="payments">
No payments detected yet.
</div>

</div>

<div class="panel">

<h2>
Session Statistics
</h2>

<div class="stats">

<div class="stat">

<h3>
USDC
</h3>

<div id="usdcStats"></div>

</div>

<div class="stat">

<h3>
EURC
</h3>

<div id="eurcStats"></div>

</div>

<div class="stat">

<h3>
cirBTC
</h3>

<div id="cirbtcStats"></div>

</div>

</div>

</div>

</div>

<script>

let monitoring = false;


async function connectWallet() {

    const wallet =
        document.getElementById(
            "wallet"
        ).value.trim();

    const response =
        await fetch(
            "/connect",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                body: JSON.stringify({
                    wallet: wallet
                })
            }
        );

    const data =
        await response.json();

    if (!data.success) {

        alert(data.error);

        return;
    }

    document.getElementById(
        "status"
    ).innerText =
        "● Connected to Arc | Chain ID: "
        + data.chain_id;

    document.getElementById(
        "status"
    ).className =
        "status connected";

    updateData();
}


async function toggleMonitor() {

    const endpoint =
        monitoring
        ? "/stop"
        : "/start";

    const response =
        await fetch(
            endpoint,
            {
                method: "POST"
            }
        );

    const data =
        await response.json();

    if (data.error) {

        alert(data.error);

        return;
    }

    monitoring =
        data.running;

    document.getElementById(
        "monitorButton"
    ).innerText =
        monitoring
        ? "Stop Monitoring"
        : "Start Monitoring";
}


async function updateData() {

    const response =
        await fetch(
            "/data"
        );

    const data =
        await response.json();

    if (!data.wallet) {

        return;
    }

    document.getElementById(
        "usdc"
    ).innerText =
        formatNumber(
            data.balances.USDC
        );

    document.getElementById(
        "eurc"
    ).innerText =
        formatNumber(
            data.balances.EURC
        );

    document.getElementById(
        "cirbtc"
    ).innerText =
        formatNumber(
            data.balances.cirBTC
        );

    renderPayments(
        data.payments
    );

    renderStats(
        "usdcStats",
        data.statistics.USDC
    );

    renderStats(
        "eurcStats",
        data.statistics.EURC
    );

    renderStats(
        "cirbtcStats",
        data.statistics.cirBTC
    );
}


function formatNumber(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "Error";
    }

    return Number(value).toFixed(8);
}


function renderPayments(
    payments
) {

    const container =
        document.getElementById(
            "payments"
        );

    if (!payments.length) {

        container.innerHTML =
            "No payments detected yet.";

        return;
    }

    container.innerHTML =
        payments.map(
            payment => {

                const className =
                    payment.direction === "IN"
                    ? "incoming"
                    : "outgoing";

                const sign =
                    payment.direction === "IN"
                    ? "+"
                    : "-";

                return `
<div class="payment">

<strong class="${className}">
${payment.direction}
${sign}${formatNumber(payment.amount)}
${payment.token}
</strong>

<div class="details">

From: ${payment.from}

<br>

To: ${payment.to}

<br>

Block: ${payment.block}

<br>

Tx: ${payment.tx}

</div>

</div>
`;

            }
        ).join("");
}


function renderStats(
    elementId,
    stats
) {

    document.getElementById(
        elementId
    ).innerHTML = `

<div class="stat-line">
Incoming: ${stats.incoming}
</div>

<div class="stat-line">
Outgoing: ${stats.outgoing}
</div>

<div class="stat-line">
Received: ${formatNumber(stats.received)}
</div>

<div class="stat-line">
Sent: ${formatNumber(stats.sent)}
</div>

`;
}


setInterval(
    updateData,
    3000
);

</script>

</body>

</html>
"""


@app.route("/")
def index():

    return render_template_string(
        HTML
    )


@app.route(
    "/connect",
    methods=["POST"]
)
def connect():

    global wallet_address

    data = request.get_json()

    address = data.get(
        "wallet",
        ""
    ).strip()

    if not Web3.is_address(address):

        return jsonify({
            "success": False,
            "error":
                "Invalid wallet address",
        })

    if not web3.is_connected():

        return jsonify({
            "success": False,
            "error":
                "Could not connect to Arc RPC",
        })

    wallet_address = (
        Web3.to_checksum_address(
            address
        )
    )

    return jsonify({
        "success": True,
        "chain_id":
            web3.eth.chain_id,
    })


@app.route(
    "/start",
    methods=["POST"]
)
def start_monitor():

    global running
    global last_block

    if not wallet_address:

        return jsonify({
            "running": False,
            "error":
                "Wallet is not connected",
        })

    if not running:

        reset_statistics()

        last_block = (
            web3.eth.block_number
        )

        running = True

        thread = threading.Thread(
            target=monitor,
            daemon=True,
        )

        thread.start()

    return jsonify({
        "running": running,
    })


@app.route(
    "/stop",
    methods=["POST"]
)
def stop_monitor():

    global running

    running = False

    return jsonify({
        "running": False,
    })


@app.route("/data")
def data():

    return jsonify({
        "wallet": wallet_address,
        "running": running,
        "balances": get_balances(),
        "payments": payments,
        "statistics": statistics,
    })


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
    )