#!/usr/bin/env python3
import argparse
import sys
from qiskit import QuantumCircuit, execute
from qiskit import BasicAer
import matplotlib.pyplot as plt

DESC = """
Finites at Fredy's esolang interpreter.
https://esolangs.org/wiki/Finites_at_Fredy%27s
"""


class Schedule:
    def __init__(self, data, storage):
        self.schedule = [night.strip() for night in data if night.strip()]
        self.storage = storage
        self.qc = QuantumCircuit(storage.size, storage.outsize)

    def circuit(self):
        """Create corresponding circuit."""
        # Select optional animatronics:
        self.storage.select()
        # Init bits
        for i, b in enumerate(self.storage.locations):
            if '(' in self.storage.raw[i]:
                self.qc.initialize([0, 1] if b else [1, 0], i)
            elif b:
                self.qc.x(i)

        # Add CSWAPs
        for i, shift in enumerate(self.schedule):
            locs = [int(v) - 1 for v in shift.split(',')]
            print(f'Night {i}: {locs}')
            self.qc.cswap(locs[1], locs[0], locs[2])

        # Add Measurements
        q = [i for i, v in enumerate(storage.raw) if '!' in v]
        self.qc.measure(q[::-1], list(range(storage.outsize)))
        print(self.qc)

    def describe(self):
        """Describe the shifts as they unfold."""
        pass

    def draw(self):
        self.qc.draw(output='mpl')
        plt.show()

    def simulate(self):
        self.circuit()

        backend = BasicAer.get_backend('qasm_simulator')
        job = execute(self.qc, backend, shots=10)
        results = job.result().get_counts(self.qc)
        print('RESULTS:', results)
        r = list(results.keys())[0]
        print('As Int:', int(r, 2))
        print('As Chr:', chr(int(r, 2)))


class Storage:
    def __init__(self, data):
        self.raw = [v.strip() for v in data.split(',')]
        self.locations = [None if 'EMPTY' in v  or '(' in v else v for v in self.raw]
        self.size = len(self.locations)
        self.outsize = data.count('!')

    def select(self):
        """
           Select optional animatronics.
           Prompts for user input.
        """
        for i, a in enumerate(self.raw):
            if '(' in a:
                ans = input(f'Is {a} present? (Y/N) ')
                if ans.upper() == 'Y':
                    self.locations[i] = a.strip('()')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=DESC, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('file', help='source file to process')
    args = parser.parse_args()

    with open(args.file, 'r') as f:
        storage = Storage(f.readline()) 
        schedule = Schedule(f.readlines(), storage)

    print('Animatronics:', storage.raw)
    print('Schedule:', schedule.schedule)

    schedule.simulate()
    print('Input Animatronics:', schedule.storage.locations)
    schedule.draw()

