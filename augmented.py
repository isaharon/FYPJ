#!/usr/bin/python3

# Query Model function for afl-fuzz.c

import os
import numpy as np
from keras.models import load_model

model = load_model("model9.h5")
max_filesize = 20480
bytesize = 8

def query_model(seed):

    # Query model for the prediction
    predictions = model.predict_classes(checkFile(seed))

    # Determine bytemask from prediction output
    # Might not need
    bytemask = get_bytemask(predictions)

    return bytemask

def vectorize(input_file):

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
            byte_pos += 1

    return shape

def vectorize_bytearray(byte_arr):

    shape = np.zeros(shape=(max_filesize, bytesize))

    #put bytearray bits into numpy array
    byte_pos = 0
    for byte in byte_arr:
        bits = bin(byte)[2:].zfill(8)
        for n, bit in enumerate(bits):
            if bit == '1':
                shape[byte_pos, n] = 1.
        byte_pos += 1

    return shape

def xor(x, y):

    xor = np.zeros(shape=(max_filesize, bytesize))

    if (x.size == y.size):
        max_size, col_size = x.shape
        for col in range(max_size):
            for bit in range(col_size):
                if x[col][bit] != y[col][bit]:
                    xor[col][bit] = 1.

    return xor

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

def get_bytemask(predictions):

    for (x, y, z), value in ndenumerate(predictions):
        if value > 0.2:
            predictions[x, y, z] = 1.
        else:
            predictions[x, y, z] = 0.

    return predictions

def diff(input_file, seed):

    diff = []

    # Get filesizes
    input_filesize = os.path.getsize(input_file)
    seed_filesize = os.path.getsize(seed)

    if input_filesize < max_filesize and seed_filesize < max_filesize:
        diff_vector = xor(input_file, seed)
        diff.append(diff_vector)
    else:
        # Get segments
        if input_filesize > seed_filesize:
            segments = get_segments(input_filesize)
        else:
            segments = get_segments(seed_filesize)

        input_ba, seed_ba = padding(input_file, seed)

        # Loop through segments
        for start in range(0, segments*max_filesize, max_filesize):
            input_segment = input_ba[start:start+max_filesize]
            seed_segment = seed_ba[start:start+max_filesize]

            input_vector = vectorize_bytearray(diff_segment)
            seed_vector = vectorize_bytearray(seed_segment)

            diff_vector = xor(input_vector, seed_vector)

            diff.append(diff_vector)

    diff = np.array(diff)
    num, filesize, features = diff.shape

    return diff.reshape(num, max_filesize//8, bytesize*8)

def is_useful(diff, bytemask):

    # Iterate diff & bytemask with bitwise AND to determine if bit is useful

    useful_bit = 0

    if (diff.size == bytemask.size):
        for (x, y, z), value in ndenumerate(diff):
            if diff[x, y, z] and bytemask[x, y, z]:
                useful_bit += 1

    if useful_bit > 10:
        return True

    return False

def get_segments(filesize):

    segments = filesize // max_filesize
    if (filesize % max_filesize) > 0:
        segments += 1

    return segments

def checkFile(input_file):

    samples = []

    input_filesize = os.path.getsize(input_file)

    if input_filesize < max_filesize:
        input_vector = vectorize(input_file)
        samples.append(input_vector)
    else:
        # Get segments needed
        segments = get_segments(input_filesize)

        # Pad file to nearest segment size
        input_ba = bytearray(open(input_file, "rb").read())

        for start in range(0, segments*max_filesize, max_filesize):
            input_segment = input_ba[start:start+max_filesize]
            input_vector = vectorize_bytearray(input_segment)
            samples.append(input_vector)

    samples = np.array(samples)

    num, filesize, features = samples.shape

    return samples.reshape(num, max_filesize//8, bytesize*8)
