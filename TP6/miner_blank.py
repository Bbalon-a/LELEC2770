
import json
import random
import binascii
import hashlib

# NOTE: run "python3 -m pip install --user requests" to get the requests
# library installed.
import requests

import canonicaljson

DIFFICULTY = 18

# TODO CHANGE YOUR NAME HERE TO SOMETHING UNIQUE!
MY_NAME = "CHANGEIT"

NODE_URL = "https://lelec2770.pythonanywhere.com"

"""
    We have left lots of opportunities for optimization.
    credit will be awarded for mining a block that adds to the main chain
    (20 FabulousCoins). Note that the faster you solve the proof of work,
    the better your chances are of landing in the main chain.

    Feel free to modify this code in any way

    We use a data representation similar to JSON to represent the blocks.
    An object is either:
    * an associative map (aka dictionnary), mapping strings to objects,
    * a list (aka sequence) of objects (may be of heterogenous types),
    * a string (sequence of unicode codepoints, encoded in UTF-8),
    * an integer (a natural number),
    * a boolean.
    In this code, we use two representations:
    * the python representations (each type of object is mapped to a python
    type: map -> dict, list -> list or tuple, string -> string, integer -> int,
    bool -> bool).
    * the canonical JSON representation: a sequence of bytes
    (specified in <http://wiki.laptop.org/go/Canonical_JSON>).
    Conversions:
    * canonical JSON -> python: json.loads
    * python -> canonical JSON: canonicaljson.dumps

    The blocks must follow the following format:
    {
        "parent_id": <parent_id: hex-encoded>,
        "miner_name": <string>,
        "nonce": <int>,
        "content": {
            "dancemove": <int in [0, .., 10]>
        }
    }
    The hash of a block is the byte string computed as the SHA256 of its
    canonical JSON representation.
    The id of a block is the hexadecimal encoding of its hash.

    ! A block is valid if
     * it contains the required fields
     * it does not contain additional fields
     * each of the fields is of the correct type
     * the dancemove is between 0 and 10 (included)
     * its hash starts with 18 '0' bits
     * the length of its canonical JSON representation is at most 10000 bytes
    ! A chain is valid if:
     * all of its blocks are valid
     * for each block, the parent_id field conains the id of the previous block
     in the chain (except for the first block, for which the parent_id should
     be the empty string).

    Good luck!
"""

# Note: the functions from the start of the file until the main() function
# are probably the most interesting to read and/or modify.


def hash_block(b):
    """Hash of the block b as a byte string."""
    return hashlib.sha256(canonicaljson.dumps(b)).digest()

def block_id(b):
    """Id of the block b (its hex-encoded SHA256 hash)."""
    return binascii.hexlify(hash_block(b)).decode('ascii')

_MSK = (0x0, 0x80, 0xc0, 0xe0, 0xf0, 0xf8, 0xfc, 0xfe)
def hash_nb_leading_zeroes(h, nb):
    """Tests if the byte string hash starts with nb bits sets at 0."""
    off=0
    while nb>=8:
        if h[off] != 0:
            return False
        nb -= 8
        off +=1
    return (h[off] & _MSK[nb]) == 0

def pow_check(block):
    """Test if the proof of work is correct."""
    return hash_nb_leading_zeroes(hash_block(block), DIFFICULTY)

def solve_block(b):
    """
    Iterate over nonces until a valid proof of work is found for the block.

    :param b: A block.

    Modify b in-place, return True if the block is solved, otherwise return
    False.

    Note: the nonce must be between 0 and 2^31-1
    """
    # @student: Is it optimal to search until you find a block (therefore
    # possibly searching for a very long time) ?
    # TODO
    return False

def reconstruct_blockchain(blocks):
    """
    Expect to receive a list of blocks.

    Output: list of lists of blocks. Each list of blocks is a reconstructed
    chain.
    """
    #TODO

def choose_chain(blockchains):
    """Choose a chain from a list of chains (each chain is a list of blocks)."""
    #TODO
    return choosen_chain

def build_block(parent_id):
    """Constructs a new block from the parent block id."""
    #TODO
    pass

def is_block_valid(block):
    return (
            type(block) == dict and
            set(block.keys()) == set(["parent_id", "miner_name", "nonce", "content"]) and
            type(block["parent_id"]) == str and
            True # TODO: add other checks...
            )

def main():
    """
    Repeatedly request all blocks from the server, then build the blockchain
    then choose the right chain to start mining the next block

    We will construct a block dictionary and pass this around to solving and
    submission functions.
    """
    # ! This is an example ! Feel free to do another strategy !
    while True:
        # Next block's parent, version, difficulty
        blocks = get_blocks()
        print("Current block list:", blocks)
        # From all blocks received from the server, reconstruct the blockchain
        blocks = [block for block in blocks if is_block_valid(block)]
        blockchains = reconstruct_blockchain(blocks)
        # Choose the right block from the blockchain
        choosen_chain = choose_chain(blockchains)
        if len(choosen_chain)==0:
            parent_block_id = ""
        else:
            parent_block_id = block_id(choosen_chain[-1])

        # Construct a block with our name in the contents that appends to the
        # head of the main chain
        new_block = build_block(parent_block_id)
        # Solve the POW
        print("Solving block", new_block)
        if solve_block(new_block):
            # Send to the server
            send_block(new_block)

def get_blocks():
    """Download all blocks from server, returns a list of blocks (in python
    representation).
    """
    response = requests.get(NODE_URL + "/blockchain/blocks/get.json")
    return json.loads(response.text)["blocks"]


def send_block(block, suggest_only=False):
    """Send solved block to server.

       return {"success": message} if add to datase
       or {"error": message} if something bad happened

       if suggest_only=True, the block is only suggested:
       the server tries it, and answers whether or not it would accept it,
       but does not add it to its database
    """
    print("Sending a valid block to server")
    if suggest_only:
        path = "/blockchain/blocks/suggest"
    else:
        path = "/blockchain/blocks/add"
    headers = {"content-type": "application/json"}
    response = requests.post(
        NODE_URL + path,
        data=canonicaljson.dumps(block),
        headers=headers,
    )
    print("response", response)
    result = response.json()
    if not suggest_only and "error" in result:
        raise ValueError("Invalid block submitted: {}".format(result["error"]))


def print_dancing_stickman():
    all_blocks = get_blocks()
    all_blocks = [block for block in all_blocks if is_block_valid(block)]
    assert len(all_blocks) > 0, "Looks like there is no blocks on the server"
    blockchains = reconstruct_blockchain(all_blocks)
    blockchain = choose_chain(blockchains)
    for block in blockchain:
        print(block["miner_name"])
        if block["content"]["dancemove"] == 0:
            print(
                """    O    
   /|\   
    |
   / \ """
            )
        elif block["content"]["dancemove"] == 1:
            print(
                """    O    
    |---   
    |
   / \ """
            )
        elif block["content"]["dancemove"] == 2:
            print(
                """    O    
 ---|   
    |
   / \ """
            )
        elif block["content"]["dancemove"] == 3:
            print(
                """   \ /   
    |   
   \|/
    O  """
            )
        elif block["content"]["dancemove"] == 4:
            print(
                """    O/   
   /|   
    |
   / \ """
            )
        elif block["content"]["dancemove"] == 5:
            print(
                """   \O    
    |\  
    |
   / \ """
            )
        elif block["content"]["dancemove"] == 6:
            print(
                """   \O/   
    |    
    |
   / \ """
            )
        elif block["content"]["dancemove"] == 7:
            print(
                """   \ /   
    |   
   \|
    O\  """
            )
        elif block["content"]["dancemove"] == 8:
            print(
                """   \ /   
    |   
    |/
   /O  """
            )
        elif block["content"]["dancemove"] == 9:
            print(
                """   \ /
    |   
    |
   /O\ """
            )
        elif block["content"]["dancemove"] == 10:
            print(""" <(^-^<) """)
        else:
            raise ValueError("The blockchain contains unvalid dancemove!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Some dummy miner for fun")
    parser.add_argument("--print_stickman", action="store_true")
    args = parser.parse_args()
    if args.print_stickman:
        print_dancing_stickman()
    else:
        main()
