"""
LELEC2770 : Privacy Enhancing Technologies

Exercice Session : Hardware Trojan

MASTER CIRCUIT
"""

from Crypto.Random import random
from minicircuit import Minicircuit, Minicircuit0, Minicircuit1, Minicircuit2

class Master():

    def __init__(self, gen_circuit, master_input):
        self.input = master_input
        self.minicircuits = [Minicircuit0(gen_circuit()), Minicircuit1(gen_circuit()), Minicircuit2(gen_circuit())]
        
    def gen_shares(self):
        input_share_0 = {}
        input_share_1 = {}
        input_share_2 = {}
        for k, v in self.input.items():
            r1 = random.getrandbits(1)
            input_share_0[k] = 0 # TO COMPLETE
            input_share_1[k] = r1 # TO COMPLETE
            input_share_2[k] = r1 ^ v # TO COMPLETE
       
        
        self.minicircuits[0].set_input(input_share_0)
        self.minicircuits[1].set_input(input_share_1)
        self.minicircuits[2].set_input(input_share_2)
    
    def run(self):
        while True:
            msg1 = self.minicircuits[1].run_step()
            msg2 = self.minicircuits[2].run_step()
            
            # When would this assert break?
            assert msg1 == msg2

            if msg1 == "finished":
                break
            elif msg1 == "multiplication_protocol":
                # TO COMPLETE
                r_all_a = self.minicircuits[0].gen_mul_r()
                r_all_b = self.minicircuits[0].gen_mul_r()
                da,db = self.minicircuits[2].mul_0(r_all_a["r1"], r_all_b["r1"])
                ea, fa, eb, fb = self.minicircuits[1].mul(r_all_a["r2"],r_all_a["r3"],r_all_a["r"],da,r_all_b["r2"],r_all_b["r3"],r_all_b["r"],db)
                self.minicircuits[2].mul_1(r_all_a["r1"],r_all_a["r4"],ea,fa,r_all_b["r1"],r_all_b["r4"],eb,fb)
            elif msg1 == "addition_protocol":
                pass


    def reconstruct_result(self):
        #Errror computation should be in 0
        #output_share_0 = self.minicircuits[0].get_output()
        output_share_1 = self.minicircuits[1].get_output()
        output_share_2 = self.minicircuits[2].get_output()
        output = {}
        for k in self.minicircuits[2].circuit.output_gates:
            output[k] = self.minicircuits[2].state[k] ^ self.minicircuits[1].state[k] # TO COMPLETE 
        return output
