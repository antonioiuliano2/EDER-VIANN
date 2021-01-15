import argparse
parser = argparse.ArgumentParser(description='select cut parameters')
parser.add_argument('--f',help="Please enter the input file location", default='n/a')
args = parser.parse_args()
print(args.f)
