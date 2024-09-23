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
from config import NUM_WORKERS, RPC_NODE_URL, PUBLIC_KEY
from rpc_client import get_block_info
from wallet import submit_block
import randomx

def construct_message(message, extra_data):
    return f"{message}_{extra_data}"

def worker(worker_id, task_queue, result_queue, stop_event):
    key_bytes = bytes.fromhex(PUBLIC_KEY)
    vm = randomx.RandomX(key_bytes, full_mem=True, secure=False, large_pages=False)
    
    while True:
        try:
            block_hash, difficulty, height = task_queue.get(timeout=1)
            if block_hash is None:  # Termination signal
                break

            nonce = 0
            while not stop_event.is_set():
                extra_data = f"{worker_id}_{nonce}"
                message = construct_message(block_hash, extra_data)
                message_bytes = message.encode()
                solution = vm(message_bytes).hex()
                if int(solution, 16) < int(difficulty, 16):
                    print(f"Worker {worker_id} found a block: {solution}, at nonce {nonce}")
                    result_queue.put({
                        "key": PUBLIC_KEY,
                        "solution": solution,
                        "message": message,
                        "extra_data": extra_data,
                        "height": height
                    })
                    break  # Break the inner loop to get new task
                nonce += 1
        except multiprocessing.queues.Empty:
            continue

def master(num_workers, initial_block_hash, initial_difficulty, initial_height):
    current_block_hash = initial_block_hash
    current_difficulty = initial_difficulty
    current_height = initial_height

    task_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()
    processes = []

    print(f"Starting {num_workers} workers...")

    for i in range(num_workers):
        p = multiprocessing.Process(target=worker, args=(i, task_queue, result_queue, stop_event))
        processes.append(p)
        p.start()

    task_queue.put((initial_block_hash, initial_difficulty, current_height))

    try:
        while True:
            time.sleep(5)
            block_info = get_block_info(RPC_NODE_URL)
            print(block_info)
            new_hash = block_info['current_hash']
            if new_hash != current_block_hash:
                print("New block found, updating workers...")

                current_block_hash = new_hash
                current_difficulty = block_info['difficulty']
                current_height = block_info['height']

                stop_event.set()  # Signal all workers to stop
                stop_event.clear()  # Clear the stop event for the next round
                task_queue.put((current_block_hash, current_difficulty, current_height))
            else:
                print("No new block found, continuing...")

            while not result_queue.empty():
                result = result_queue.get()
                try : 
                    res = submit_block(result)
                    print(res)
                    stop_event.clear()
                except Exception as e:
                    print(f"Failed to submit block: {e}")
    except KeyboardInterrupt:
        print("Stopping mining...")
        stop_event.set()

    for p in processes:
        p.join()

if __name__ == "__main__":
    initial_block_info = get_block_info(RPC_NODE_URL)
    initial_block_hash = initial_block_info['current_hash']
    initial_difficulty = initial_block_info['difficulty']
    height = initial_block_info['height']

    master(NUM_WORKERS, initial_block_hash, initial_difficulty, height)