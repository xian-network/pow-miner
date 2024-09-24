import currency

height = Variable()
current_hash = Variable()
difficulty = Variable()
last_block_time = Variable()
solutions = Hash()
base_reward = Variable()


@construct
def seed():
    random.seed()
    height.set(0)
    initial_hash = hex(random.randint(0, 2**256 - 1))
    difficulty.set(initial_hash)
    current_hash.set(initial_hash)
    last_block_time.set(now)
    base_reward.set(5)


@export
def submit_it(
    key: str, extra_data: str, solution: str, solution_height: int
):
    current_height = height.get()

    assert solution_height == current_height, "Wrong block height"
    assert len(extra_data) < 100, "Extra data is too long"
    assert len(key) == 64, "Key is not 64 characters"
    assert len(solution) == 64, "Solution is not 64 characters"

    current_difficulty = difficulty.get()

    # Verify the submitted hash
    if int(solution, 16) < int(current_difficulty, 16):
        computed_hash = compute_hash(key, current_hash.get(), extra_data)
        assert computed_hash == solution, "Hash does not match solution"
        reward_amount = calculate_reward()
        solutions[current_height] = {
            "problem": current_hash.get(),
            "extra_data": extra_data,
            "key": key,
            "solution": solution,
            "timestamp": now,
            "difficulty": current_difficulty,
            "reward_amount": reward_amount,
        }
        retarget_difficulty()
        height.set(current_height + 1)
        current_hash.set(solution)
        last_block_time.set(now)
        currency.transfer(amount=reward_amount, to=ctx.caller)
        return True
    return False


def compute_hash(key: str, message: str, extra_data: str):
    full_message = construct_message(message, extra_data)
    computed_hash = crypto.randomx_hash(key, full_message)
    return computed_hash


def calculate_reward():
    stamps_hash = ForeignHash(foreign_contract="stamp_cost", foreign_name="S")
    stamp_cost = stamps_hash['value']
    xian_txn_cost = 1400 / stamp_cost # 1400 per randomx hash submission
    reward_amount = xian_txn_cost + base_reward.get()
    return reward_amount


def construct_message(message, extra_data):
    return f"{message}_{extra_data}"


def retarget_difficulty():
    current_height = height.get()
    if current_height % 3 == 0 and current_height > 0:  # Retarget every 5 blocks
        time_taken = (now - solutions[current_height - 3]['timestamp']).seconds
        expected_time = 2 * 60 * 3  # 5 blocks * 2 minutes per block
        adjustment_factor = time_taken / expected_time
        new_difficulty = int(int(difficulty.get(),16) * adjustment_factor)
        difficulty.set(hex(new_difficulty))
