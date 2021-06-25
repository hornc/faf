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

    def circuit(self):
        """Create corresponding circuit."""
        pass

    def describe(self):
        """Describe the shifts as they unfold."""
        pass


class Storage:
    def __init__(self, data):
        self.raw = [v.strip() for v in data.split(',')]
        self.locations = [None if 'EMPTY' in v  or '(' in v else v for v in self.raw]
        self.size = len(self.locations)
        self.outsize = data.count('!')

    def select(self):
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

    # Select optional animatronics:
    storage.select()
    print('Animatronics:', storage.locations)

    qc = QuantumCircuit(storage.size, storage.outsize)
    # Init bits
    for i, b in enumerate(storage.locations):
        if '(' in storage.raw[i]:
            qc.initialize([0, 1] if b else [1, 0], i)
        elif b:
            qc.x(i)

    # Add CSWAPs
    for i, shift in enumerate(schedule.schedule):
        locs = [int(v) - 1 for v in shift.split(',')]
        print(f'Night {i}: {locs}')
        qc.cswap(locs[1], locs[0], locs[2])

    # Add Measurements
    q = [i for i, v in enumerate(storage.raw) if '!' in v]
    qc.measure(q[::-1], list(range(storage.outsize)))

    print(qc)
    #qc.measure_all()

    backend = BasicAer.get_backend('qasm_simulator')
    job = execute(qc, backend, shots=10)
    results = job.result().get_counts(qc)
    print('RESULTS:', results)
    r = list(results.keys())[0]
    print('As Int:', int(r, 2))
    print('As Chr:', chr(int(r, 2)))

    qc.draw(output='mpl')
    plt.show()

