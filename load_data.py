#!/usr/bin/python3

# Program to load a numpy file
# Display data stored in numpy array

import numpy as np
import os
import argparse

# Display full numpy array
np.set_printoptions(threshold=np.nan)

def main():

    parser = argparse.ArgumentParser(description="Load numpy file and display its data in numpy array.")
    parser.add_argument("input_file", help="numpy file to load and display data from")
    
    args = parser.parse_args()

    # Check if file exists and is valid
    if not os.path.isfile(args.input_file):
        print("[-] " + args.input_file + " does not exists.")
        exit(0)
    elif not args.input_file.lower().endswith('.npy'):
        print("[-] " + args.input_file + " is an invalid file.")
        exit(0)

    input_file = args.input_file
    np_data = np.load(input_file)
    print(np_data[0][:32])
    print(np_data[3][:32])
    print(np_data[5][:32])
    samples, max_filesize, num_of_features = np_data.shape
    new_data = np_data.reshape((samples, 512, 64))
    print(new_data[0][:2])
    print(new_data[3][:2])
    print(new_data[5][:2])
    print(new_data.shape)
    if (new_data[0] == new_data[3]).all():
        print("Match")

if __name__ == '__main__':
    main()
