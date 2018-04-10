#!/usr/bin/python3

import os
import argparse
import re
import numpy as np

def saveToFile(sample_x, sample_y, output_file):

    np.save(output_file + "_x", sample_x)
    np.save(output_file + "_y", sample_y)

    return 0

# Given numpy array of x and y, x ^ y
def xor(x, y):

    xor = np.zeros(shape=(4096, 8))

    if (x.size == y.size):
        max_size, col_size = x.shape
        for byte in range(max_size):
            for col in range(col_size):
                if x[byte][col] != y[byte][col]:
                    xor[byte][col] = 1.
    else:
        print("[-] Unable to perform xor due to shape.")
    
    return xor

def xor_vectorize(x, y):

    #np.zeros shape
    shape = np.zeros(shape=(4096, 8))

    x_b = bytearray(open(x, "rb").read())
    y_b = bytearray(open(y, "rb").read())

    if (len(x_b) > len(y_b)):
        size = len(x_b)
        diff = size - len(y_b)
        y_b = y_b.ljust(size, b'\x00')
    elif (len(x_b) < len(y_b)):
        size = len(y_b)
        diff = size - len(x_b)
        x_b = x_b.ljust(size, b'\x00')
    else:
        size = len(x_b)
    
    print(len(x_b), len(y_b))

    xor_bytes = bytearray(size)

    for i in range(size):
        xor_bytes[i] = x_b[i] ^ y_b[i]

    byte_pos = 0
    for x in xor_bytes:
        byte = x
        bits = bin(byte)[2:].zfill(8)
        for n, bit in enumerate(bits):
            if bit == '1':
                shape[byte_pos, n] = 1.
        byte_pos = byte_pos + 1

    return shape

# Vectorize data from given file
def vectorize(input_file):

    #np.zeros shape
    shape = np.zeros(shape=(4096, 8))

    with open(input_file, "rb") as f:
        byte = f.read(1)
        byte_pos = 0
        while byte:
            bits = bin(int.from_bytes(byte, byteorder="big"))[2:].zfill(8)
            for n, bit in enumerate(bits):
                if bit == '1':
                    shape[byte_pos, n] = 1.
            byte = f.read(1)
            byte_pos = byte_pos + 1

    return shape

def checkDirectory(folder, x, y):

    print("[+] Checking directory: " + folder)

    skip_counter = 0
    for f in sorted(os.listdir(folder)):
        f = os.path.join(folder, f)
        # Check size of file vectorize or skip accordingly
        if "orig:" in f:
            x_file = f
            x_vector = vectorize(x_file)
        elif "+cov" in f:
            y_file = f
            if os.path.getsize(y_file) < 4096:
                # TODO implement better design
                #y_vector = xor_vectorize(x_file, y_file)
                y_vector = vectorize(y_file)
                y_vector = xor(x_vector, y_vector)
                x.append(x_vector)
                y.append(y_vector)
            else:
                skip_counter = skip_counter + 1
                # Get segments needed for file
                # Pad x_file
                # Loop through segments
                # Vectorize and append sequentially
    print("Skipped " + str(skip_counter) + " files. Yet to implement segmentation.")

    return x, y

# Check input directory
def checkDirectories(folders):

    final_x = []
    final_y = []

    for folder in folders:
        x = []
        y = []
        x, y = checkDirectory(folder, x, y)
        final_x.extend(x)
        final_y.extend(y)

    final_x = np.array(final_x)
    final_y = np.array(final_y)

    return final_x, final_y

def main():

    parser = argparse.ArgumentParser(description='Gather input, code coverage dataset from AFL output directory.') 
    parser.add_argument("-i", "--input-dir", required=True, dest="input_dir", help="master directory to collect dataset pair from", metavar="INPUT_DIR")
    parser.add_argument("-o", "--output-file", required=True, dest="output_file", help="output filename", metavar="OUTPUT_FILE")

    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print("[-] " + args.input_dir + " does not exist.")
        exit(0)

    if not os.access(args.input_dir, os.R_OK):
        print("[-] " + args.input_dir + " access denied.")
        exit(0)

    # Argument vectors into variables
    input_dir = os.path.abspath(args.input_dir)
    folders = next(os.walk(input_dir))[1]
    for i in range(0, len(folders)):
        folders[i] = os.path.join(input_dir, folders[i])

    filepath = os.path.join(os.curdir, args.output_file)
    output_file = os.path.abspath(filepath)

    # check folder
    sample_x, sample_y = checkDirectories(folders)

    if (sample_x.size and sample_y.size):
        saveToFile(sample_x, sample_y, output_file)

    return 0

if __name__ == '__main__':
    main()
