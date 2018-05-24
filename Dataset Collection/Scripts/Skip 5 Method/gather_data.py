#!/usr/bin/python3

import random
import os
import argparse
import numpy as np

max_filesize = 20480
bytesize = 8

def saveToFile(sample_x, sample_y, output_file):

    np.savez_compressed(output_file, x=sample_x, y=sample_y)
    print("[+] Dataset stored in: " + output_file + ".npz")
    
    return 0

# Given numpy array of x and y, x ^ y
def xor(x, y):

    xor = np.zeros(shape=(max_filesize, bytesize))

    if (x.size == y.size):
        max_size, col_size = x.shape
        for col in range(max_size):
            for bit in range(col_size):
                if x[col][bit] != y[col][bit]:
                    xor[col][bit] = 1.
    else:
        print("[-] Unable to perform xor due to shape.")
    
    return xor

# Return padded bytearray of files
def padding(x, y):

    x_ba = bytearray(open(x, "rb").read())
    y_ba = bytearray(open(y, "rb").read())

    #check bigger file and pad to its size
    if (len(x_ba) > len(y_ba)):
        size = len(x_ba)
        y_ba = y_ba.ljust(size, b'\x00')
    elif (len(x_ba) < len(y_ba)):
        size = len(y_ba)
        x_ba = x_ba.ljust(size, b'\x00')

    return x_ba, y_ba

# Vectorize data from given file
def vectorize(input_file):

    #np.zeros shape
    shape = np.zeros(shape=(max_filesize, bytesize))

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

# Vectorize data from given byte array of file
def vectorize_bytearray(byte_arr):

    #np.zeros shape
    shape = np.zeros(shape=(max_filesize, bytesize))

    #put bytearray bits into numpy array
    byte_pos = 0
    for byte in byte_arr:
        bits = bin(byte)[2:].zfill(8)
        for n, bit in enumerate(bits):
            if bit == '1':
                shape[byte_pos, n] = 1.
        byte_pos = byte_pos + 1

    return shape

def get_segments(x, y):

    if x > y:
        filesize = x
    else:
        filesize = y
    
    segments = filesize // max_filesize
    if (filesize % max_filesize) > 0:
        segments = segments + 1

    return segments

def checkDirectory(folder):

    print("[+] Checking directory: " + os.path.basename(folder))
    
    x = []
    y = []

    files = sorted(os.listdir(folder))

    data_counter = 0
    file_counter = 0
    skip_counter = 5

    for f in files:
        f = os.path.join(folder, f)
        # Check name of file vectorize or skip accordingly
        # orig/orig: due to change when copying folder
        #file_counter += 1
        skip_counter += 1

        if "orig" in f:
            x_file = f
            x_filesize = os.path.getsize(x_file)
        elif "+cov" in f:
            if skip_counter > 5:
                y_file = f
                y_filesize = os.path.getsize(y_file)
                if y_filesize < max_filesize and x_filesize < max_filesize:
                    # Vectorize y then x ^ y and store in y
                    x_vector = vectorize(x_file)
                    y_vector = vectorize(y_file)
                    y_vector = xor(x_vector, y_vector)
                    x.append(x_vector)
                    y.append(y_vector)
                else:
                    # Get segments for bigger file
                    segments = get_segments(x_filesize, y_filesize)

                    # Pad file to whichever is bigger in size
                    x_ba, y_ba = padding(x_file, y_file)

                    #Loop through segments
                    for start in range(0, segments*max_filesize, max_filesize):
                        # Vectorize and append sequentially
                        x_segment = x_ba[start:start+max_filesize]
                        y_segment = y_ba[start:start+max_filesize]

                        x_vector = vectorize_bytearray(x_segment)
                        y_vector = vectorize_bytearray(y_segment)
                        # x ^ y
                        y_vector = xor(x_vector, y_vector)

                        x.append(x_vector)
                        y.append(y_vector)

                # Reset and add counters
                data_counter += 1
                skip_counter = random.randint(0,5)

    print("[+] Done!")
    print("[-] No. of data collected: " + str(data_counter))

    return x, y

# Check input directory
def checkDirectories(folders):

    final_x = []
    final_y = []

    for folder in sorted(folders):
        x, y = checkDirectory(folder)
        final_x.extend(x)
        final_y.extend(y)

    final_x = np.array(final_x)
    final_y = np.array(final_y)

    x_samples, filesize, num_of_features = final_x.shape
    y_samples, filesize, num_of_features = final_y.shape

    final_x, final_y = final_x.reshape(x_samples, max_filesize//8, bytesize*8), final_y.reshape(y_samples, max_filesize//8, bytesize*8)

    print("[+] Total samples collected: " + str(x_samples) + "/" + str(y_samples))

    return final_x, final_y

def main():
    global character_level
    global token_index
    global max_filesize

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
