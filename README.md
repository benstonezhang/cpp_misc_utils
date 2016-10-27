# Useful script to handle C/C++ header/source files.

## StructFormat
python script to parse C/C++ header files and generate C++ code for formatting data of struct

###Usage
Run below command:
```
cd Samples
python ../Gen_StructFormatter.py sample_const.h sample_datatype.h sample_struct.h
```
new files will be generated in the `Samples` folder:
```
StructFormatter.cpp
StructFormatter.h
```
