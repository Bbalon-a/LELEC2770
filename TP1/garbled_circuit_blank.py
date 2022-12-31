"""
LELEC2770 : Privacy Enhancing Technologies

Exercice Session : Secure 2-party computation

Garbled Circuit
"""

import os
import random # Insecure randomness, better to use from "secrets" on python >= 3.6

from aes import AES
import OT
from logic_circuit import Gate

def garble_circuit(circuit, myinputs):
    """Garble a circuit

    :param circuit: circuit to garble
    :type circuit: logic_circuit.Circuit
    :param myinputs: already known inputs, to be hidden
    :type myinputs: dictionnary {gate_id: 0/1}
    :return: Garbled circuit, ungarbling keys associated to myinputs and OT
        senders for other inputs.
    :rtype: (garbled_table, input_keys, ot_senders)

    - garbled_table: dictionnary {gate_id: 4*[AES_key]}
    - input_keys: dictionnary {input_gate_id: AES_key}
    - ot_senders: dictionnary {input_gate_id: OT.Sender}

    @student: What are the key steps in this function that make it such that
    the inputs of Alice are not revealed to Bob ?
    """
    # Garbling keys (k_0, k_1) for each gate => secret
    output_table = {}
    # Garbled table for each gate => public
    garbled_table = {}
    # Ungarbling keys associated to my inputs => public
    input_keys = {}
    # OT senders for inputs of the other guy => public
    ot_senders = {}

    # ---- Input validation ----
    for g_id, g_value in myinputs.items():
        assert circuit.g[g_id].kind == "INPUT"
        assert g_value in (0, 1)

    # ---- Garbling keys generation ----
    for g_id in circuit.g:
        # For output gates, we encrypt the binary output instead of an AES key.
        if not g_id in circuit.output_gates:
            k_0 = _random_key()
            k_1 = _random_key()
            output_table[g_id] = (k_0, k_1)

    # ---- Garbled tables generation ----
    for g_id, gate in circuit.g.items():
        # We already retrieved the values for all the input gates.
        if gate.kind != "INPUT":
            K_0 = output_table[gate.in0_id]  # K_0 = k_00, k_01
            K_1 = output_table[gate.in1_id]  # K_1 = k_10, k_11
            c_list = []
            for i in range(2):
                for j in range(2):
                    # 'real' evaluation of the gate on i,j
                    alpha = Gate.compute_gate(gate.kind, i, j)
                    if g_id in circuit.output_gates:
                        m = _encode_int(alpha)  # 0 or 1
                    else:
                        K = output_table[g_id]
                        m = _encode_key(K[alpha])  # k_0 or k_1 (see above)
                    c = AES(_encode_key(K_1[j])).encrypt(m)
                    c_ij = AES(_encode_key(K_0[i])).encrypt(c)
                    c_list.append(c_ij)
            # @students: Why is it important to shuffle the list?
            random.shuffle(c_list)
            garbled_table[g_id] = c_list

    # ---- Ungarbling keys generation for my inputs ----
    for g_id, input_val in myinputs.items():
        K = output_table[g_id]
        key = K[input_val]  # key = K[i] where i in [0,1] is my input
        input_keys[g_id] = key

    # ---- Oblivious transfer senders ----
    for g_id, gate in circuit.g.items():
        if gate.kind == "INPUT" and g_id not in myinputs:
            k0, k1 = output_table[g_id]
            ot_senders[g_id] = OT.Sender(k0, k1)
    return (garbled_table, input_keys, ot_senders)


def evaluate_garbled_circuit(circuit, myinputs, garbled_table, input_keys, ot_senders):
    """Evaluate a garbled circuit

    :param circuit: circuit to evaluate
    :type circuit: logic_circuit.Circuit
    :param myinputs: known inputs, to be kept hidden
    :type myinputs: dictionnary {gate_id: 0/1}
    :param garbled_table: Table of grabled logic gates
    :type garbled_table: dictionnary {gate_id: 4*[AES_key]}
    :param input_keys: ungarbling keys already known
    :type input_keys: dictionnary {input_gate_id: AES_key}
    :param ot_senders: OT senders to recover missing input keys using myinputs
        values
    :return: State of the evaluated circuit
    :rtype: dictionnary {gate_id: gate_output_value}

    @student: What are the key steps in this function that make it such that
    the inputs of Bob are not revealed to Alice ?
    """
    state = input_keys.copy()
    # ---- Input validation ----
    for g_id, g_value in myinputs.items():
        assert circuit.g[g_id].kind == "INPUT"
        assert g_value in (0, 1)
    assert set(ot_senders) == set(myinputs)

    # ---- make OTs, store resulting keys in state ----
    for g_id, myinput_value in myinputs.items():
        raise NotImplemented() # TODO
        # state[g_id] = ... [response from the OT]

    # ---- Recursive ungarbling ----
    def _evaluate_garbled_gate_rec(g_id):
        """Return the output of the gate."""
        # Hint to do AES decryption (AES-DEC): AES(_encode_key(key)).decrypt(ciphertext)
        if g_id in state:
            return state[g_id]
        # Evaluate the inputs of the gate (by recursive call), then evaluate
        # the garbled gate.
        # The un-garbling key (or evaluation result) for the gate g_id should
        # be stored in state[g_id].
        # Hint: use the _decode_decryption function
        raise NotImplemented() # TODO

    for g_id in circuit.output_gates:
        _evaluate_garbled_gate_rec(g_id)

    return state


INT_MARKER = 13*b'\x00' + b'\x01'
KEY_MARKER = 14*b'\x00'

def _encode_int(x):
    """Encode integer before encryption"""
    # '+' operation on byte strings means concatenation
    return x.to_bytes(2, byteorder='big') + INT_MARKER


def _encode_key(key):
    """Encode AES key before encryption"""
    # '+' operation on byte strings means concatenation
    assert isinstance(key, bytes) and len(key) == 2
    return key + KEY_MARKER


def _decode_decryption(d):
    """Check if a decryption is valid and convert it to the right output
    format.

    :param d: decrypted text
    :type d: bytes
    :rtype: int (0/1), AES_key or None if the decryption is invalid
    """
    assert isinstance(d, bytes) and len(d) == 16
    if d[2:] == INT_MARKER:
        return int.from_bytes(d[:2], byteorder='big')
    elif d[2:] == KEY_MARKER:
        return d[:2]
    else:
        # @students: When is this branch taken ?
        return None

def _random_key():
    return os.urandom(2)
