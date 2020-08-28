import argparse

parser = argparse.ArgumentParser()
# parser.add_argument('echo', help='echo helps to understand;')
parser.add_argument('square', type=int, help='display a square of a given number;')
parser.add_argument('--verbosity', help='increase output verbosity;')

args = parser.parse_args()
print(args.square**2)

if args.verbosity:
    print("verbosity turned on")
