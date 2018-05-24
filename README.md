# FYPJ
Software Vulnerability Analysis and Discovery using Deep Neural Network

Information
----------------
- Augmented afl-fuzz - contains the afl-fuzz incorporated with the neural network and additional original sources
- Dataset collection - Dataset gathering scripts, compressed .npz datasets used, seed files used to fuzz
- Jupyter Notebooks - training of neural network
- Models - models trained in .h5 format

Dependencies
------------
- Keras
- Tensorflow
- numpy

Command used to fuzz and run afl-fuzz
----------------
`afl-fuzz -i <seed file input dir> -o <output dir> <readelf program> -a @@`

>Standard commands to run afl-fuzz with addition of -a parameter used for the readelf which displays all information.
>Note: @@ is a placeholder and has to be included when running the augmented afl-fuzz segfault occurs.
