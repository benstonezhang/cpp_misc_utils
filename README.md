# Libraris and scripts to make coder's life easy :-)

## [StructFormat](struct)
python script to parse C/C++ header files and generate C++ code for formatting data of struct.

The parser of data type and struct is based on regular expression, not grammar. So it can only process code of regular complexity factor and normal code style, not the complex one.

主要作用就是根据头文件里面定义的数据类型和结构，自动生成相应的格式化输出函数。通常我们使用第三方C/C++库开发的时候，第三方的头文件里面都会定义很多的数据类型，但是往往又没有提供相应的格式化输出函数，导致我们调试的时候不得不自己写格式化输出函数，费时费力。这个工具主要也就是省了自己写一大堆无聊的 printf 函数的时间。

## [Anonymous semaphore on OSX](osx)
The apple's OSX does not support anonymous semaphore, but we often need it when our code will run on both Linux and OSX. This routine give a workaround for this issue.
