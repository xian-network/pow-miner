# Miner which searches for blocks on the xian blockchain.
# Xian is a DPoS blockchain which uses PoW contract mining as a form of token distribution.

"""
Miner requirements :

1. Miner should be started from the CLI.
2. CLI start takes arguments such as :
    a. Number of threads to use for mining.
    b. Wallet address to use for mining.
    c. The RPC node URL to connect to.
    d. The contract name to mine on.
3. Miner needs to query the contract for the current block hash, height and difficulty.
4. Miner will use the RandomX algorithm to mine the next block.
5. When the miner finds a block, it will submit the block to the contract.
"""

import multiprocessing
import time
from config import NUM_WORKERS, RPC_NODE_URL
from rpc_client import get_block_info, submit_block
from utils import simulate_mining

def worker(worker_id, task_queue, result_queue, stop_event):
    while not stop_event.is_set():
        try:
            block_hash, difficulty = task_queue.get(timeout=1)
            result = simulate_mining(worker_id, block_hash, difficulty, stop_event)
            result_queue.put(result)
        except multiprocessing.queues.Empty:
            continue

def master(num_workers, initial_block_hash, initial_difficulty):
    task_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()
    processes = []

    for i in range(num_workers):
        p = multiprocessing.Process(target=worker, args=(i, task_queue, result_queue, stop_event))
        processes.append(p)
        p.start()

    task_queue.put((initial_block_hash, initial_difficulty))

    try:
        while True:
            time.sleep(5)
            block_info = get_block_info(RPC_NODE_URL)
            new_block_found = block_info['new_block_found']
            if new_block_found:
                new_block_hash = block_info['block_hash']
                new_difficulty = block_info['difficulty']
                print("New block found, updating workers...")
                stop_event.set()
                stop_event.clear()
                task_queue.put((new_block_hash, new_difficulty))

            while not result_queue.empty():
                result = result_queue.get()
                print(result)

    except KeyboardInterrupt:
        print("Stopping mining...")
        stop_event.set()

    for p in processes:
        p.join()

if __name__ == "__main__":
    initial_block_info = get_block_info(RPC_NODE_URL)
    initial_block_hash = initial_block_info['block_hash']
    initial_difficulty = initial_block_info['difficulty']

    master(NUM_WORKERS, initial_block_hash, initial_difficulty)