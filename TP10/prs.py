"""
LELEC2770 : Privacy Enhancing Technologies

Exercice Session : Hardware Trojan

Paper - Rock - Scissors
"""

from Crypto.Random import random
from logic_circuit import Gate, Circuit, INPUT_GATE
from master import Master

def gen_prs_circuit():
    prs_circuit = Circuit(
        {
            "A": INPUT_GATE,
            "B": INPUT_GATE,
            "C": INPUT_GATE,
            "D": INPUT_GATE,
            "AB": Gate("AND", "A", "B"),
            "AC": Gate("AND", "A", "C"),
            "BC": Gate("AND", "B", "C"),
            "BxC": Gate("XOR", "B", "C"),
            "BD": Gate("AND", "B", "D"),
            "CD": Gate("AND", "C", "D"),
            "AD": Gate("AND", "A", "D"),
            "AxD": Gate("XOR", "A", "D"),
            "ACxBD": Gate("XOR", "AC", "BD"),
            "BCxCD": Gate("XOR", "BC", "CD"),
            "ABxAD": Gate("XOR", "AB", "AD"),
            "ACxBDxBCxCD": Gate("XOR", "ACxBD", "BCxCD"),
            "ACxBDxABxAD": Gate("XOR", "ACxBD", "ABxAD"),
            "E": Gate("XOR", "ACxBDxABxAD", "BxC"),
            "F": Gate("XOR", "ACxBDxBCxCD", "AxD"),
        },
        {"E", "F"},
    )
    return prs_circuit


def choice_to_bin(choice):
    if choice in ["PAPER", "P"]:
        return 0, 0
    elif choice in ["ROCK", "R"]:
        return 1, 0
    elif choice in ["SCISSORS", "S"]:
        return 0, 1
    elif choice in ["LOSE", "L"]:
        return 1, 1


def prs_result(E, F):
    if (E, F) == (0, 0):
        return "draw"
    elif (E, F) == (0, 1):
        return "Bob wins"
    elif (E, F) == (1, 0):
        return "Alice wins"
    else:
        raise ValueError((E, F))


def test_prs_circuit():
    inputs = {"P": (0, 0), "R": (1, 0), "S": (0, 1), "L": (1, 1)}
    for ai_n, ai in inputs.items():
        for bi_n, bi in inputs.items():
            input_all = {"A": ai[0], "B": ai[1], "C": bi[0], "D": bi[1]}
            M = Master(gen_prs_circuit, input_all)
            M.gen_shares()
            M.run()
            res = M.reconstruct_result()
            #print(ai_n, bi_n, prs_result(*res))
            ref_res = gen_prs_circuit().evaluate(input_all).state
            assert (ref_res['E'], ref_res['F']) == (res['E'], res['F'])

test_prs_circuit()

print("TESTS ARE PASSED :)")

