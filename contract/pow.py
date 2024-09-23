height = Variable()
current_hash = Variable()
difficulty = Variable()
last_block_time = Variable()
solutions = Hash()


@construct
def seed():
    height.set(0)
    random.seed()
    difficulty.set(1)
    current_hash.set(hex(random.randint(0, 2**256 - 1)))
    last_block_time.set(now)


@export
def submit_it(
    key: str, message: str, extra_data: str, solution: str, solution_height: int
):
    current_height = height.get()

    assert solution_height == current_height + 1, "Block height is not the next block"
    assert len(message) < 100, "Message is too long"
    assert len(extra_data) < 100, "Extra data is too long"
    assert len(key) == 64, "Key is not 64 characters"
    assert len(solution) == 64, "Solution is not 64 characters"

    current_difficulty = difficulty.get()

    # Verify the submitted hash
    if int(solution, 16) < current_difficulty:
        computed_hash = compute_hash(key, current_hash.get(), extra_data)
        assert computed_hash == solution, "Hash does not match solution"
        solutions[current_height] = {
            "solution": solution,
            "timestamp": now,
            "message": message,
            "extra_data": extra_data,
            "vk": key,
            "difficulty": current_difficulty,
        }
        height.set(current_height + 1)
        last_block_time.set(now)
        current_hash.set(solution)
        retarget_difficulty()
        return True
    return False


def compute_hash(key: str, message: str, extra_data: str):
    full_message = construct_message(message, extra_data)
    computed_hash = crypto.randomx_hash(key, full_message)
    return computed_hash


def construct_message(message, extra_data):
    return f"{message}_{extra_data}"


def retarget_difficulty():
    current_height = height.get()
    if current_height % 10 == 0 and current_height > 0:  # Retarget every 10 blocks
        time_taken = (now - last_block_time.get()).total_seconds()
        expected_time = 10 * 2 * 60  # 10 blocks * 2 minutes per block
        adjustment_factor = expected_time / time_taken
        new_difficulty = difficulty.get() * adjustment_factor
        difficulty.set(max(1, int(new_difficulty)))  # Ensure difficulty is at least 1
