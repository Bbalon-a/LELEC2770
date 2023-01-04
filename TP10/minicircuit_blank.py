"""
LELEC2770 : Privacy Enhancing Technologies

Exercice Session : Hardware Trojan

MINICIRCUIT
"""

from queue import Queue
from Crypto.Random import random

class Minicircuit():

    def __init__(self, circuit):
        self.circuit = circuit
        self.state = {}
        self.eval_order = None

    def set_input(self, input_share):
        self.input = input_share 
        for k, v in input_share.items():
            self.state[k] = v 

    def _recursive_evaluate(self, g_id):
        if g_id not in self.state:
            self.state[g_id] = None
            
            in0_id = self.circuit.g[g_id].in0_id
            in1_id = self.circuit.g[g_id].in1_id
            
            self._recursive_evaluate(in0_id)
            self._recursive_evaluate(in1_id)

            self.eval_order.put(g_id)


    def run_step(self):
        if self.eval_order is None:
            self.eval_order = Queue()
            for g_id in self.circuit.output_gates:
                self._recursive_evaluate(g_id)

        if self.eval_order.empty():
            return "finished"
        else:
            curr_g_id = self.eval_order.get()
            in0_id = self.circuit.g[curr_g_id].in0_id
            in1_id = self.circuit.g[curr_g_id].in1_id

            if self.circuit.g[curr_g_id].kind == "AND":
                self.curr_in = [self.state[in0_id], self.state[in1_id]]   
                self.curr_g_id = curr_g_id
                return "multiplication_protocol"
            elif self.circuit.g[curr_g_id].kind == "XOR":
                self.state[curr_g_id] = self.add(self.state[in0_id], self.state[in1_id])
                return "addition_protocol"
        
    def get_output(self):
        output = {}
        for g_id in self.circuit.output_gates:
            output[g_id] = self.state[g_id]
        return output 

class Minicircuit0(Minicircuit):

    def __init__(self, circuit):
        super().__init__(circuit)

    def gen_mul_r(self):
        ri = [random.getrandbits(1)] * 4

        return {"r1": ri[0], 
                "r2": ri[1],
                "r3": ri[2],
                "r4": ri[3],
                "r": None # TO COMPLETE}

class Minicircuit1(Minicircuit):
    def __init__(self, circuit):
        super().__init__(circuit)

    def add(self, in_0, in_1):
        return None # TO COMPLETE 

    def mul(self, r2a, r3a, ra, da, r2b, r3b, rb, db):
        ea = None # TO COMPLETE
        eb = None # TO COMPLETE
        fa = None # TO COMPLETE
        fb = None # TO COMPLETE

        self.state[self.curr_g_id] = None # TO COMPLETE
        return ea, fa, eb, fb

class Minicircuit2(Minicircuit):
    def __init__(self, circuit):
        super().__init__(circuit)

    def add(self, in_0, in_1):
        return None # TO COMPLETE 

    def mul_0(self, r1a, r1b):
        da = None # TO COMPLETE
        db = None # TO COMPLETE

        return da, db
    
    def mul_1(self, r1a, r4a, ea, fa, r1b, r4b, eb, fb):
        self.state[self.curr_g_id] = None # TO COMPLETE
