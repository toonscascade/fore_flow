import json
from pathlib import Path
from eth_account import Account
from web3 import Web3

ROOT_DIR = Path(__file__).resolve().parent.parent
ABI_PATH = ROOT_DIR / "abi" / "ThreatEvidence.json"
BIN_PATH = ROOT_DIR / "abi" / "ThreatEvidence.bin"

PROVIDER_URL = "http://127.0.0.1:8545"
CHAIN_ID = 31337
# Hardhat account #0
PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"


def deploy():
    w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))
    if not w3.is_connected():
        raise RuntimeError("Cannot connect to blockchain provider at " + PROVIDER_URL)

    with open(ABI_PATH, "r") as f:
        abi = json.load(f)

    with open(BIN_PATH, "r") as f:
        bytecode = f.read().strip()

    account = Account.from_key(PRIVATE_KEY)
    print(f"Deploying from account: {account.address}")

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(account.address)

    tx = contract.constructor().build_transaction({
        "from": account.address,
        "nonce": nonce,
        "chainId": CHAIN_ID,
        "gas": 3_000_000,
        "gasPrice": w3.eth.gas_price,
    })

    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"Deployment tx sent: {tx_hash.hex()}")

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
    contract_address = receipt.contractAddress
    print(f"\n========================================================")
    print(f"ThreatEvidence contract deployed at: {contract_address}")
    print(f"Block number: {receipt.blockNumber}")
    print(f"Gas used: {receipt.gasUsed}")
    print(f"========================================================\n")

    # Quick test anchor
    test_contract = w3.eth.contract(address=contract_address, abi=abi)
    sample_hash = bytes.fromhex("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
    anchor_tx = test_contract.functions.anchorEvidence(sample_hash).build_transaction({
        "from": account.address,
        "nonce": nonce + 1,
        "chainId": CHAIN_ID,
        "gas": 200_000,
        "gasPrice": w3.eth.gas_price,
    })
    signed_anchor = account.sign_transaction(anchor_tx)
    a_tx_hash = w3.eth.send_raw_transaction(signed_anchor.raw_transaction)
    w3.eth.wait_for_transaction_receipt(a_tx_hash, timeout=30)

    is_anchored = test_contract.functions.isAnchored(sample_hash).call()
    print(f"Test anchor verification on-chain: {is_anchored}")

    return contract_address


if __name__ == "__main__":
    deploy()
