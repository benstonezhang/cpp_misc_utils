//
// Created by Benstone on 16/10/26.
//

#ifndef SAMPLE_STRUCT_H
#define SAMPLE_STRUCT_H

typedef struct struct_foo1
{
	short GlobalID;												//
	char Address[128];											//
	TypeFooChar9	_ID;										//
	bool IsAvailable;											//
	double Percentage;											//
	short Max[CONST_FOO_4];
	double Min[CONST_FOO_3];
	EnumFoo2 Type[CONST_FOO_1];	//
} STRUCT_FOO1;

typedef struct struct_foo2
{
	short GlobalID;				//
	char Address[128];			//
	TypeFooChar9	_ID;
	bool bIsUsing;
} STRUCT_FOO2;

struct struct_foo3
{
	EnumFoo1 Type;

	STRUCT_FOO1 tdParam[CONST_FOO_1];
	short tdParam_count;

	STRUCT_FOO2 mdParam[CONST_FOO_2];
	short mdParam_count;

	short LowLimitms;
	short UpLimitms;
};

#endif //SAMPLE_STRUCT_H
