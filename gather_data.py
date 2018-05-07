#!/usr/bin/python3

import random
import os
import argparse
import numpy as np
from itertools import zip_longest

max_filesize = 30720
chunksize = 8
character_level = False
token_index = None

def saveToFile(sample_x, sample_y, output_file):

    np.savez_compressed(output_file, x=sample_x, y=sample_y)
    print("[+] Dataset stored in: " + output_file + ".npz")
    
    return 0

# Given numpy array of x and y, x ^ y
def xor(x, y):

    xor = np.zeros(shape=(max_filesize, chunksize))

    if (x.size == y.size):
        max_size, col_size = x.shape
        for byte in range(max_size):
            for col in range(col_size):
                if x[byte][col] != y[byte][col]: xor[byte][col] = 1.
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
    shape = np.zeros(shape=(max_filesize, chunksize))

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
    shape = np.zeros(shape=(max_filesize, 8))

    #put bytearray bits into numpy array
    byte_pos = 0
    for byte in byte_arr:
        bits = bin(byte)[2:].zfill(8)
        for n, bit in enumerate(bits):
            if bit == '1':
                shape[byte_pos, n] = 1.
        byte_pos = byte_pos + 1

    return shape

def get_token_index():

    token_index = {}

    # Generate all possible 8-bit characters
    characters = ''
    for i in range(0, 256):
        characters += chr(i)

    # Populate token index with characters in binary
    for n, character in enumerate(characters):
        character = character.encode('UTF-8')
        token_index[character] = n + 1

    return token_index

def one_hot_encoding(input_file):

    #np.zeros shape
    shape = np.zeros(shape=(max_filesize, 256))

    with open(input_file, "rb") as f:
        byte = f.read(1)
        byte_pos = 0
        while byte:
            index = token_index.get(byte)
            shape[byte_pos, index] = 1.
            byte = f.read(1)
            byte_pos += 1

    return shape

def one_hot_encoding_bytearray(byte_arr):

    #np.zeros shape
    shape = np.zeros(shape=(max_filesize, 256))

    #put bytearray bits into numpy array
    byte_pos = 0
    for index in byte_arr:
        if index > 0:
            shape[byte_pos, index] = 1.
            byte_pos += 1

    return shape

def character_xor(x_ba, y_ba):
    
    xor = np.zeros(shape=(max_filesize, 256))
    
    byte_pos = 0
    if len(x_ba) == len(y_ba):
        for char_x, char_y in zip_longest(x_ba, y_ba, fillvalue=0):
            index = char_x ^ char_y
            if index > 0:
                xor[byte_pos, index] = 1.
            byte_pos += 1

    return xor

def get_segments(filesize):

    segments = filesize // max_filesize
    if (filesize % max_filesize) > 0:
        segments = segments + 1

    return segments

def checkDirectory(folder):

    print("[+] Checking directory: " + folder)
    
    x = []
    y = []

    files = sorted(os.listdir(folder))

    data_counter = 0
    skip_counter = 5

    for f in files:
        f = os.path.join(folder, f)
        # Check name of file vectorize or skip accordingly
        # orig/orig: due to change when copying folder

        if "orig" in f:
            x_file = f
            x_filesize = os.path.getsize(x_file)
        elif "+cov" in f:
            # Get out of loop once certain sample size reached
            if data_counter > 99:
                break

            skip_counter += 1
            if skip_counter > 5:
                y_file = f
                y_filesize = os.path.getsize(y_file)
                if y_filesize < max_filesize and x_filesize < max_filesize:
                    if character_level:
                        x_vector = one_hot_encoding(x_file)
                        x_ba = bytearray(open(x_file, "rb").read())
                        y_ba = bytearray(open(y_file, "rb").read())
                        y_vector = character_xor(x_ba, y_ba)
                    else:
                        # Vectorize y then x ^ y and store in y
                        x_vector = vectorize(x_file)
                        y_vector = vectorize(y_file)
                        y_vector = xor(x_vector, y_vector)
                    x.append(x_vector)
                    y.append(y_vector)
                else:
                    # Get segments needed for file
                    segments = get_segments(y_filesize)

                    # Pad file to whichever is bigger in size
                    x_ba, y_ba = padding(x_file, y_file)

                    #Loop through segments
                    for start in range(0, segments*max_filesize, max_filesize):
                        # Vectorize and append sequentially
                        x_segment = x_ba[start:start+max_filesize]
                        y_segment = y_ba[start:start+max_filesize]

                        if character_level:
                            x_vector = one_hot_encoding_bytearray(x_segment)
                            y_vector = character_xor(x_segment, y_segment)
                        else:
                            x_vector = vectorize_bytearray(x_segment)
                            y_vector = vectorize_bytearray(y_segment)
                            # x ^ y
                            y_vector = xor(x_vector, y_vector)

                        x.append(x_vector)
                        y.append(y_vector)

                data_counter += 1
                skip_counter = random.randint(0,5)

    print("[+] Done!")

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

    return final_x, final_y

def main():
    global character_level
    global token_index
    global max_filesize

    parser = argparse.ArgumentParser(description='Gather input, code coverage dataset from AFL output directory.') 
    parser.add_argument("-i", "--input-dir", required=True, dest="input_dir", help="master directory to collect dataset pair from", metavar="INPUT_DIR")
    parser.add_argument("-o", "--output-file", required=True, dest="output_file", help="output filename", metavar="OUTPUT_FILE")
    parser.add_argument("-c", "--character-encoding", dest="char_encoding", help="use character level encoding", action="store_true")

    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print("[-] " + args.input_dir + " does not exist.")
        exit(0)

    if not os.access(args.input_dir, os.R_OK):
        print("[-] " + args.input_dir + " access denied.")
        exit(0)

    if args.char_encoding:
        character_level = True
        token_index = get_token_index()
        max_filesize = 4096

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
