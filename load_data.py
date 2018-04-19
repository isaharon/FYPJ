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
    elif not args.input_file.lower().endswith('.npz'):
        print("[-] " + args.input_file + " is an invalid file.")
        exit(0)

    input_file = args.input_file
    np_data = np.load(input_file)
    dataset_x = np_data['x']
    dataset_y = np_data['y']
    print(dataset_x[0][:32])
    print(dataset_x[3][:32])
    print(dataset_x[5][:32])
    samples, max_filesize, num_of_features = dataset_x.shape
    new_x = dataset_x.reshape((samples, 512, 64))
    print(new_x[0][:2])
    print(new_x[3][:2])
    print(new_x[5][:2])
    print(new_x.shape)
    print(new_x.dtype)
    if (new_x[0] == new_x[3]).all():
        print("Match")

if __name__ == '__main__':
    main()
