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
    x_dataset = np_data['x']
    y_dataset = np_data['y']
    print(x_dataset.shape, y_dataset.shape)
    num, timestep, num_of_features = x_dataset.shape

    # Check if x dataset is equal and different
    t = 0
    f = 0
    first_sample = 0

    for i in range(0, num):
        if np.array_equal(x_dataset[first_sample], x_dataset[i]):
            t += 1
        else:
            t += 1
            f += 1
            first_sample = i
    print("Files checked: ", t)
    print("Variety: ", f+1)

if __name__ == '__main__':
    main()
