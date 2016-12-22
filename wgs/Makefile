CFLAGS=-std=gnu11 -Wall -fPIC

lib: libwgs_utils.a

libwgs_utils.a: wgs_utils.o
	ar -cr $@ $?

test: wgs_utils.c
	gcc ${CFLAGS} -o $@ -DWGS_UTILS_TEST $^

.c.o:
	gcc ${CFLAGS} -c -o $@ $<

wgs_utils.c: wgs_utils.h

all: lib test

clean:
	rm -f test *.a *.o

