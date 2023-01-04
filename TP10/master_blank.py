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
            input_share_0[k] = None # TO COMPLETE
            input_share_1[k] = None # TO COMPLETE
            input_share_2[k] = None # TO COMPLETE
       
        
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
                pass
            elif msg1 == "addition_protocol":
                pass


    def reconstruct_result(self):
        output_share_0 = self.minicircuits[0].get_output()
        output_share_1 = self.minicircuits[1].get_output()
        output_share_2 = self.minicircuits[2].get_output()

        output = {}
        for k in self.minicircuits[0].circuit.output_gates:
            output[k] = None # TO COMPLETE 
        return output
