//
// Created by Benstone on 16/10/26.
//

#ifndef SAMPLE_DATATYPE_H
#define SAMPLE_DATATYPE_H

typedef char TypeFooChar9[9];

typedef enum : char {
	EnumFoo1_a	= 'a',
	EnumFoo1_b	= 'b',
	EnumFoo1_c	= 'c',
} EnumFoo1;

typedef enum
{
	EnumFoo2_1 = 0x01, // some comments
	EnumFoo2_2 =    0x02,
	EnumFoo2_3 = 0x03,
	EnumFoo2_4			= 0x04
} EnumFoo2;

enum EnumFoo3 : char {
	EnumFoo3_x = 'x',
	EnumFoo3_y  = 'y',
	EnumFoo3_z	= 'z',
};

enum EnumFoo4
{
	EnumFoo4_1			= 0x01, // some comments
	EnumFoo4_2			= 0x02,
	EnumFoo4_3,
	EnumFoo4_4
};

#endif //SAMPLE_DATATYPE_H
