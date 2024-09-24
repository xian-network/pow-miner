import requests

def query():
    return """
    query MyQuery {
        difficulty: allStates(filter: { key: { equalTo: "con_pow_better2.difficulty" } }) {
            nodes {
            value
            }
        }
        height: allStates(filter: { key: { equalTo: "con_pow_better2.height" } }) {
            nodes {
            value
            }
        }
        current_hash: allStates(filter: { key: { equalTo: "con_pow_better2.current_hash" } }) {
            nodes {
            value
            }
        }
        last_block_time: allStates(filter: { key: { equalTo: "con_pow_better2.last_block_time" } }) {
            nodes {
            value
            }
        }
    }
"""

def get_block_info(rpc_node_url):
    response = requests.post(f"{rpc_node_url}/graphql", json={"query": query()})
    if response.status_code == 200:
        
        json = response.json()
        last_block_time = json['data']['last_block_time']['nodes'][0]['value']
        height = json['data']['height']['nodes'][0]['value']
        current_hash = json['data']['current_hash']['nodes'][0]['value']
        difficulty = json['data']['difficulty']['nodes'][0]['value']
        
        return {
            'last_block_time': last_block_time,
            'height': height,
            'current_hash': current_hash,
            'difficulty': difficulty
        }

    else:
        raise Exception(f"Failed to get block info: {response.status_code} {response.text}")

if __name__ == "__main__":
    print(get_block_info("https://testnet.xian.org/graphql"))