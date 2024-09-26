## XIAN POW Miner

** THIS IS A WORK IN PROGRESS, NOT WORKING YET **

A proof of work miner for the XIAN blockchain.

Currently a proof of concept, working on testnet.

## Usage

### Installation

```bash
# Clone the repository
git clone https://github.com/xian-network/pow-miner.git

# create a virtual environment and activate it
python3 -m venv venv
source venv/bin/activate

# install the dependencies
pip install -r requirements.txt
```

### Configuration

- Create a Xian wallet, using the [browser extension](https://chromewebstore.google.com/detail/xian-wallet/kcimjjhplbcgkcnanijkolfillgfanlc) or [xian-py](https://pypi.org/project/xian-py/)
- Populate your wallet address and private key in `miner/config.py`
- Change `NUM_WORKERS` to the number of worker threads you want to use for mining. (default 1)
- You will need to obtain some testnet Xian to to submit your blocks and verify your results.
- Ask in the [Xian Telegram](https://t.me/xian_network) for testnet Xian.

### Running

```bash
# Start the miner
python miner.py
```