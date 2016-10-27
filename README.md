# Useful script to handle C/C++ header/source files.

## StructFormat
python script to parse C/C++ header files and generate C++ code for formatting data of struct.

The parser of data type and struct is based on regular expression, not grammar. So it can only process code of regular complexity factor and normal code style, not the complex one.

主要作用就是根据头文件里面定义的数据类型和结构，自动生成相应的格式化输出函数。通常我们使用第三方C/C++库开发的时候，第三方的头文件里面都会定义很多的数据类型，但是往往又没有提供相应的格式化输出函数，导致我们调试的时候不得不自己写格式化输出函数，费时费力。这个工具主要也就是省了自己写一大堆无聊的 printf 函数的时间。

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
