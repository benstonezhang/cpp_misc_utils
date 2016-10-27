all: run-test

test: StructFormatter.h StructFormatter.cpp main.cpp
	g++ -std=c++11 -o test StructFormatter.cpp main.cpp

run-test: test
	./test

