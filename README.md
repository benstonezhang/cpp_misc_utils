# Useful script to handle C/C++ header/source files.

## StructFormat
python script to parse C/C++ header files and generate C++ code for formatting data of struct

###Usage
Run below command:
```
cd Samples
python ../Gen_StructFormatter.py sample_const.h sample_datatype.h sample_struct.h
```
some convenient method will be generated in the new files at `Samples` folder:
```
StructFormatter.cpp
StructFormatter.h
```
The formatter method is mimic standard library function `sprintf`, below is a example:
```
int StructFormatter::sprint(char *buf, const char *prefix, const STRUCT_FOO1 *p)
```
