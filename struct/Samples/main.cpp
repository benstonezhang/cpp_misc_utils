#include <cstring>
#include <cstdio>
#include "StructFormatter.h"

int main(int argc, char *argv[])
{
	char buf[40960];
	struct struct_foo3 foo;
	memset(&foo, 0, sizeof(foo));
	StructFormatter::sprint(buf, "", &foo);
	puts(buf);
}
