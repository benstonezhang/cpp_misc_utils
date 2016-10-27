#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2016 by Benstone Zhang. All rights reserved.
#

import sys
import re

script_name = re.match(r'.*/([\w\.]+)', sys.argv[0]).groups()[0]

hdr_files = sys.argv[1:]

cpp_class_name = 'StructFormatter'
hpp_file = cpp_class_name + '.h'
cpp_file = cpp_class_name + '.cpp'

const_def = {}
type_def = {}
enum_def = {}
enum_type_def = {}
struct_def = {}
struct_name_list = []
msg_name_list = []
struct_size = {}
struct_item_name_length = {}
struct_name_len = 0

re_mul = re.compile(r'(\S*)\s*\*\s*(\S*)')


# Standardize data type, also calculate the size of it
def get_data_type(name, size):
    if name.startswith('unsigned'):
        type_name = 'u'
    else:
        type_name = ''

    if name.endswith('short'):
        type_name += 'int16_t'
    elif name.endswith('int'):
        type_name += 'int32_t'
    elif name.endswith('long'):
        type_name += 'int64_t'

    if len(type_name) > 0:
        name = type_name

    item = [name]

    while type_def.get(name) is not None:
        type_info = type_def.get(name)
        name = type_info[0]
        dim_info = []
        for s in type_info[1:]:
            dim_info.extend([int(s)])
        if len(dim_info) > 0:
            for s in dim_info:
                item.insert(1, s)

    item_size = len(item)
    item[0] = name

    for s in size:
        if re_mul.match(s):
            # here the size of array is present as "x * y"
            mul_str = re_mul.match(s).groups()
            x = mul_str[0]
            y = mul_str[1]
            while const_def.get(x) is not None:
                x = const_def[x]
            while const_def.get(y) is not None:
                y = const_def[y]
            s = int(x) * int(y)
            item.insert(item_size, s)
        else:
            while const_def.get(s) is not None:
                s = const_def[s]
            item.insert(item_size, int(s))

    return tuple(item)


# Regular Expression to parse C/C++ header

# comments
re_comments_cpp = re.compile(r'^\s*//')
re_comments_cpp_remove = re.compile(r'\s*//.*')
re_comments_c_1 = re.compile(r'^/\*')
re_comments_c_2 = re.compile(r'^\*')

# macro
re_define_func = re.compile(r'^#define\s+\S+\(')
re_define = re.compile(r'^#define\s+(\S+)\s+(.+)\s*$')
re_define_mul = re.compile(r'^#define\s+(\S+)\s+\(\s*(\S+)\s*\*\s*(\S+)\s*\)\s*$')

# bracket
re_brackets = re.compile(r'\((.*)\)')

# array
re_array_type = re.compile(r'^typedef\s+(.+)\s+(\w+)\s*\[\s*(\d+)\s*\]\s*;')
re_array2_type = re.compile(r'^typedef\s+(.+)\s+(\w+)\s*\[\s*(\d+)\s*\]\s*\[\s*(\d+)\s*\]\s*;')
re_data_type = re.compile(r'^typedef\s+(.+)\s+(\w+)\s*;')

# enum
re_enum_type_start = re.compile(r'^typedef\s+enum\s+')
re_enum_type_start_with_type = re.compile(r'^typedef\s+enum.*:\s*(\S+)')
re_enum_type_item = re.compile(r'^\s*(\w+)\s*=\s*(\'*\w+\'*)\s*,')
re_enum_type_end = re.compile(r'^\}\s*(\w+)\s*;')

re_enum_type_start2 = re.compile(r'^enum\s+(\S+)\s*')
re_enum_type_start2_with_type = re.compile(r'^enum\s+\S+\s*:\s*(\S+)')
re_enum_type_item2 = re.compile(r'^\s*(\w+)\s*,*')
re_enum_type_end2 = re.compile(r'^\}\s*;')

# struct begin
re_struct_type_start = re.compile(r'^typedef\s+struct\s+')
re_struct_type_start2 = re.compile(r'^struct\s+(\S+)')
# 2D array of field
re_struct_type_array2_item = re.compile(r'^(\w+)\s+(\w+)\s*\[\s*(.*)\s*\]\s*\[\s*(.*)\s*\]')
# 1D array of field
re_struct_type_array_item = re.compile(r'^(\w+)\s+(\w+)\s*\[\s*(.*)\s*\]')
# field
re_struct_type_item = re.compile(r'^(\w+)\s+(\w+)\s*')
# struct end
re_struct_type_end = re.compile(r'^\}\s*(\w+)\s*')
re_struct_type_end2 = re.compile(r'^\}\s*')


for hdr_file in hdr_files:
    # Read the header file
    with open(hdr_file) as hdr:
        while True:
            line = hdr.readline()
            if len(line) == 0:
                break

            line = line.strip()

            if re_comments_cpp.match(line) or \
               re_comments_c_1.match(line) or \
               re_comments_c_2.match(line) or \
               re_define_func.match(line):
                continue

            # concat multi-line expression
            while line.endswith('\\'):
                line += hdr.readline().strip()

            define = re_define_mul.match(line)
            if define is not None:
                # there is multiplication in the macro
                arrays = define.groups()
                x = re_brackets.sub(r'\1', arrays[1])
                while const_def.get(x):
                    x = re_brackets.sub(r'\1', const_def[x])
                y = re_brackets.sub(r'\1', arrays[2])
                while const_def.get(y):
                    y = re_brackets.sub(r'\1', const_def[y])
                const_def[arrays[0]] = str(int(x) * int(y))
                continue

            define = re_define.match(line)
            if define is not None:
                pair = define.groups()
                s = re_brackets.sub(r'\1', pair[1])
                while const_def.get(s):
                    s = re_brackets.sub(r'\1', const_def[s])
                const_def[pair[0]] = s
                continue

            array2_type = re_array2_type.match(line)
            if array2_type is not None:
                # 2D array
                arrays = array2_type.groups()
                type_def[arrays[1]] = get_data_type(arrays[0], arrays[2:])
                continue

            array_type = re_array_type.match(line)
            if array_type is not None:
                # 1D array
                arrays = array_type.groups()
                type_def[arrays[1]] = get_data_type(arrays[0], arrays[2:])
                continue

            data_type = re_data_type.match(line)
            if data_type is not None:
                pair = data_type.groups()
                type_def[pair[1]] = get_data_type(pair[0], ())
                continue

            enum_type = re_enum_type_start.match(line)
            if enum_type is not None:
                # typedef of enum

                # for C++11, the data type can be specified for enum
                enum_data_type = re_enum_type_start_with_type.match(line)
            else:
                enum_type = re_enum_type_start2.match(line)
                if enum_type is not None:
                    # enum
                    enum_name = enum_type.groups()[0]

                    # for C++11, the data type can be specified for enum
                    enum_data_type = re_enum_type_start2_with_type.match(line)

            if enum_type is not None:
                if enum_data_type is not None:
                    enum_type_name = get_data_type(enum_data_type.groups()[0], ())[0]
                else:
                    enum_type_name = 'int32_t'

                items = []
                last_value = None

                while True:
                    line = hdr.readline()
                    enum_type = re_enum_type_end.match(line)
                    if enum_type is not None:
                        enum_name = enum_type.groups()[0]
                    else:
                        enum_type = re_enum_type_end2.match(line)
                    if enum_type is not None:
                        enum_def[enum_name] = items
                        enum_type_def[enum_name] = enum_type_name
                        break
                    enum_type = re_enum_type_item.match(line)
                    if enum_type is not None:
                        pair = enum_type.groups()
                        items.append((pair[0], pair[1]))
                        last_value = pair[1]
                    else:
                        enum_type = re_enum_type_item2.match(line)
                        if enum_type is not None:
                            pair = enum_type.groups()
                            if type(last_value) is str:
                                if last_value.startswith('0x'):
                                    last_value = int(last_value, 16)
                                else:
                                    last_value = int(last_value)
                            last_value += 1
                            items.append((pair[0], str(last_value)))
                continue

            # here is struct
            struct_type = re_struct_type_start.match(line)
            if struct_type is None:
                struct_type = re_struct_type_start2.match(line)
                if struct_type is not None:
                    struct_name = struct_type.groups()[0]

            if struct_type is not None:
                items = []
                struct_end = False

                item_name_length = 0

                while True:
                    line = hdr.readline().strip()
                    if re_comments_cpp.match(line) is not None:
                        continue

                    for subline in re_comments_cpp_remove.sub('', line).split(';'):
                        subline = subline.strip()
                        if len(subline) == 0:
                            continue

                        arrays = None

                        struct_type = re_struct_type_end.match(subline)
                        if struct_type is None:
                            struct_type = re_struct_type_end2.match(subline)
                        if struct_type is not None:
                            # end of struct definition
                            if len(struct_type.groups()) > 0:
                                struct_name = str(struct_type.groups()[0])

                            if len(struct_name) > struct_name_len:
                                struct_name_len = len(struct_name)

                            struct_def[struct_name] = items
                            struct_name_list.append(struct_name)

                            msg_name_list.append(struct_name)
                            struct_item_name_length[struct_name] = item_name_length

                            struct_end = True
                            break

                        # check every member of struct
                        item_type = re_struct_type_array2_item.match(subline)
                        if item_type is None:
                            item_type = re_struct_type_array_item.match(subline)
                            if item_type is None:
                                item_type = re_struct_type_item.match(subline)
                                if item_type is None:
                                    continue

                        # handle data type of struct member
                        arrays = item_type.groups()
                        type_name = arrays[0]
                        item_name = arrays[1]
                        data_type = get_data_type(type_name, arrays[2:])
                        type_name = data_type[0]

                        if len(item_name) > item_name_length:
                            item_name_length = len(item_name)

                        items.append((item_name, data_type))

                    if struct_end is True:
                        break
            continue

del re_comments_cpp
del re_comments_cpp_remove
del re_comments_c_1
del re_comments_c_2

del re_define_func
del re_define
del re_define_mul
del re_brackets

del re_array_type
del re_array2_type
del re_data_type

del re_enum_type_start
del re_enum_type_item
del re_enum_type_end

del re_struct_type_start
del re_struct_type_array2_item
del re_struct_type_array_item
del re_struct_type_item
del re_struct_type_end


if True:
    with open(hpp_file, 'w') as hdr:
        with open(cpp_file, 'w') as cpp:
            hdr.write('''/*
 * !!! DO NOT EDIT. !!!
 *
 * Generated by script ''' + script_name + '''
 */

#ifndef __''' + cpp_class_name.upper() + '''_H
#define __''' + cpp_class_name.upper() + '''_H

#ifndef __cplusplus
#error "Only C++ is supported by now"
#endif

#include <cstdint>

''')
            for hdr_file in hdr_files:
                hdr.write('#include "' + hdr_file + '"\n')
            hdr.write('''

class ''' + cpp_class_name + ''' {
public:''')

            cpp.write('''/*
 * !!! DO NOT EDIT. !!!
 *
 * Generated by script ''' + script_name + '''
 */

#include <sys/time.h>
#include <string.h>
#include <stdio.h>

#include "''' + cpp_class_name + '''.h"
''')

            hdr_bufs = ['']
            cpp_bufs = ['']
            for enum_name in enum_def:
                enum_type = enum_def[enum_name]
                hdr_bufs.append('	static int sprint(char *buf, const ' + enum_name + ' value);')
                cpp_bufs.append('int ' + cpp_class_name + '::sprint(char *buf, const ' + enum_name + ' value) {')
                cpp_bufs.append('	const char *name = "N/A";')
                cpp_bufs.append('	switch(value) {')
                for enum_item in enum_type:
                    cpp_bufs.append('		case ' + enum_item[0] + ':')
                    cpp_bufs.append('			name = "' + enum_item[0] + '";')
                    cpp_bufs.append('			break;')
                cpp_bufs.append('	}')
                cpp_bufs.append('	return sprintf(buf, "%s(%d)\\n", name, value);')
                cpp_bufs.append('}\n')
            hdr_bufs.append('')
            hdr.write('\n'.join(hdr_bufs))
            cpp.write('\n'.join(cpp_bufs))

            hdr_bufs = ['']
            cpp_bufs = ['']
            for struct_name in struct_name_list:
                hdr_bufs.append('	static int sprint(char *buf, const char *prefix, const ' + struct_name + ' *p);')
                cpp_bufs.append('int ' + cpp_class_name + '::sprint(char *buf, const char *prefix, const ' + struct_name + ' *p) {')
                cpp_bufs.append('	int len = sprintf(buf, "%s' + struct_name + '\\n", prefix);')

                prefix_updated = False
                for item in struct_def[struct_name]:
                    item_type = item[1][0]

                    if prefix_updated is False:
                        if struct_def.get(item_type) is not None or len(item[1]) > 2 or (len(item[1]) > 1 and item_type not in ('char', 'unsigned char')):
                            cpp_bufs.append('	char prefix2[strlen(prefix) + 2];')
                            cpp_bufs.append('	strcpy(prefix2, prefix);')
                            cpp_bufs.append('	strcat(prefix2, "\\t");')
                            prefix_updated = True

                    if struct_def.get(item_type) is not None:
                        if len(item[1]) == 1:
                            cpp_bufs.append('	len += sprintf(buf + len, "%s' + item[0] + ':\\n", prefix);')
                            cpp_bufs.append('	len += sprint(buf + len, prefix2, &(p->' + item[0] + '));')
                        elif len(item[1]) == 2:
                            cpp_bufs.append('	for (int i=0; i<' + str(item[1][1]) + '; i++) {')
                            cpp_bufs.append('		len += sprintf(buf + len, "%s' + item[0] + '[%d]:\\n", prefix, i);')
                            cpp_bufs.append('		len += sprint(buf + len, prefix2, &(p->' + item[0] + '[i]));')
                            cpp_bufs.append('	}')
                        else:
                            cpp_bufs.append('	for (int i=0; i<' + str(item[1][1]) + '; i++) {')
                            cpp_bufs.append('		for (int j=0; j<' + str(item[1][2]) + '; j++) {')
                            cpp_bufs.append('			len += sprintf(buf + len, "%s' + item[0] + '[%d][%d]:\\n", prefix, i, j);')
                            cpp_bufs.append('			len += sprint(buf + len, prefix2, &(p->' + item[0] + '[i][j]));')
                            cpp_bufs.append('		}')
                            cpp_bufs.append('	}')

                    elif enum_def.get(item_type) is not None:
                        if len(item[1]) == 1:
                            cpp_bufs.append('	len += sprintf(buf + len, "%s%-' + str(struct_item_name_length[struct_name]) + 's: ", prefix, "' + item[0] + '");')
                            cpp_bufs.append('	len += sprint(buf + len, p->' + item[0] + ');')
                        elif len(item[1]) == 2:
                            cpp_bufs.append('	len += sprintf(buf + len, "%s%-' + str(struct_item_name_length[struct_name]) + 's:\\n", prefix, "' + item[0] + '");')
                            cpp_bufs.append('	for (int i=0; i<' + str(item[1][1]) + '; i++) {')
                            cpp_bufs.append('		strcat(buf + len, prefix2);')
                            cpp_bufs.append('		len += strlen(prefix2);')
                            cpp_bufs.append('		len += sprint(buf + len, p->' + item[0] + '[i]);')
                            cpp_bufs.append('	}')
                        else:
                            cpp_bufs.append('	len += sprintf(buf + len, "%s%-' + str(struct_item_name_length[struct_name]) + 's:\\n", prefix, "' + item[0] + '");')
                            cpp_bufs.append('	for (int i=0; i<' + str(item[1][1]) + '; i++) {')
                            cpp_bufs.append('		for (int j=0; j<' + str(item[1][2]) + '; j++) {')
                            cpp_bufs.append('			strcat(buf + len, prefix2);')
                            cpp_bufs.append('			len += strlen(prefix2);')
                            cpp_bufs.append('			len += sprint(buf + len, p->' + item[0] + '[i][j]);')
                            cpp_bufs.append('		}')
                            cpp_bufs.append('	}')

                    if len(item[1]) > 2:
                        if item_type in ('char', 'unsigned char'):
                            cpp_bufs.append('	len += sprintf(buf + len, "%s' + item[0] + ':\\n", prefix);')
                            cpp_bufs.append('	for (int i=0; i<' + str(item[1][2]) + '; i++) {')
                            cpp_bufs.append('		len += sprintf(buf + len, "%s%s\\n", prefix2, p->' + item[0] + '[i]);')
                            cpp_bufs.append('	}')
                        elif item_type == 'bool':
                            cpp_bufs.append('	len += sprintf(buf + len, "%s' + item[0] + 's:", prefix);')
                            cpp_bufs.append('	for (int i=0; i<' + str(item[1][1]) + '; i++) {')
                            cpp_bufs.append('		for (int j=0; j<' + str(item[1][2]) + '; j++) {')
                            cpp_bufs.append('			len += sprintf(buf + len, " %s", p->' + item[0] + '[i][j] ? "True" : "False");')
                            cpp_bufs.append('		}')
                            cpp_bufs.append('		len += sprintf(buf + len, "\\n");')
                            cpp_bufs.append('	}')
                        elif item_type in ('int8_t', 'int16_t', 'int32_t'):
                            cpp_bufs.append('	len += sprintf(buf + len, "%s' + item[0] + 's:", prefix);')
                            cpp_bufs.append('	for (int i=0; i<' + str(item[1][1]) + '; i++) {')
                            cpp_bufs.append('		for (int j=0; j<' + str(item[1][2]) + '; j++) {')
                            cpp_bufs.append('			len += sprintf(buf + len, "%d", p->' + item[0] + '[i][j]);')
                            cpp_bufs.append('		}')
                            cpp_bufs.append('		len += sprintf(buf + len, "\\n");')
                            cpp_bufs.append('	}')
                        elif item_type in ('uint8_t', 'uint16_t', 'uint32_t'):
                            cpp_bufs.append('	len += sprintf(buf + len, "%s' + item[0] + 's:", prefix);')
                            cpp_bufs.append('	for (int i=0; i<' + str(item[1][1]) + '; i++) {')
                            cpp_bufs.append('		for (int j=0; j<' + str(item[1][2]) + '; j++) {')
                            cpp_bufs.append('			len += sprintf(buf + len, "%u", p->' + item[0] + '[i][j]);')
                            cpp_bufs.append('		}')
                            cpp_bufs.append('		len += sprintf(buf + len, "\\n");')
                            cpp_bufs.append('	}')
                        elif item_type == 'int64_t':
                            cpp_bufs.append('	len += sprintf(buf + len, "%s' + item[0] + 's:", prefix);')
                            cpp_bufs.append('	for (int i=0; i<' + str(item[1][1]) + '; i++) {')
                            cpp_bufs.append('		for (int j=0; j<' + str(item[1][2]) + '; j++) {')
                            cpp_bufs.append('			len += sprintf(buf + len, "%lld", p->' + item[0] + '[i][j]);')
                            cpp_bufs.append('		}')
                            cpp_bufs.append('		len += sprintf(buf + len, "\\n");')
                            cpp_bufs.append('	}')
                        elif item_type == 'uint64_t':
                            cpp_bufs.append('	len += sprintf(buf + len, "%s' + item[0] + 's:", prefix);')
                            cpp_bufs.append('	for (int i=0; i<' + str(item[1][1]) + '; i++) {')
                            cpp_bufs.append('		for (int j=0; j<' + str(item[1][2]) + '; j++) {')
                            cpp_bufs.append('			len += sprintf(buf + len, "%llu", p->' + item[0] + '[i][j]);')
                            cpp_bufs.append('		}')
                            cpp_bufs.append('		len += sprintf(buf + len, "\\n");')
                            cpp_bufs.append('	}')
                        elif item_type in ('float', 'double'):
                            cpp_bufs.append('	len += sprintf(buf + len, "%s' + item[0] + 's:", prefix);')
                            cpp_bufs.append('	for (int i=0; i<' + str(item[1][1]) + '; i++) {')
                            cpp_bufs.append('		for (int j=0; j<' + str(item[1][2]) + '; j++) {')
                            cpp_bufs.append('			len += sprintf(buf + len, "%f", p->' + item[0] + '[i][j]);')
                            cpp_bufs.append('		}')
                            cpp_bufs.append('		len += sprintf(buf + len, "\\n");')
                            cpp_bufs.append('	}')
                    elif len(item[1]) > 1:
                        if item_type in ('char', 'unsigned char'):
                            cpp_bufs.append('	len += sprintf(buf + len, "%s%-' + str(struct_item_name_length[struct_name]) + 's: %s\\n", prefix, "' + item[0] + '", p->' + item[0] + ');')
                        elif item_type == 'bool':
                            cpp_bufs.append('	len += sprintf(buf + len, "%s' + item[0] + 's:", prefix);')
                            cpp_bufs.append('	for (int i=0; i<' + str(item[1][1]) + '; i++) {')
                            cpp_bufs.append('		len += sprintf(buf + len, " %s", p->' + item[0] + '[i] ? "True" : "False");')
                            cpp_bufs.append('	}')
                            cpp_bufs.append('	len += sprintf(buf + len, "\\n");')
                        elif item_type in ('int8_t', 'int16_t', 'int32_t'):
                            cpp_bufs.append('	len += sprintf(buf + len, "%s' + item[0] + 's:", prefix);')
                            cpp_bufs.append('	for (int i=0; i<' + str(item[1][1]) + '; i++) {')
                            cpp_bufs.append('		len += sprintf(buf + len, "%d", p->' + item[0] + '[i]);')
                            cpp_bufs.append('	}')
                            cpp_bufs.append('	len += sprintf(buf + len, "\\n");')
                        elif item_type in ('uint8_t', 'uint16_t', 'uint32_t'):
                            cpp_bufs.append('	len += sprintf(buf + len, "%s' + item[0] + 's:", prefix);')
                            cpp_bufs.append('	for (int i=0; i<' + str(item[1][1]) + '; i++) {')
                            cpp_bufs.append('		len += sprintf(buf + len, "%u", p->' + item[0] + '[i]);')
                            cpp_bufs.append('	}')
                            cpp_bufs.append('	len += sprintf(buf + len, "\\n");')
                        elif item_type == 'int64_t':
                            cpp_bufs.append('	len += sprintf(buf + len, "%s' + item[0] + 's:", prefix);')
                            cpp_bufs.append('	for (int i=0; i<' + str(item[1][1]) + '; i++) {')
                            cpp_bufs.append('		len += sprintf(buf + len, "%lld", p->' + item[0] + '[i]);')
                            cpp_bufs.append('	}')
                            cpp_bufs.append('	len += sprintf(buf + len, "\\n");')
                        elif item_type == 'uint64_t':
                            cpp_bufs.append('	len += sprintf(buf + len, "%s' + item[0] + 's:", prefix);')
                            cpp_bufs.append('	for (int i=0; i<' + str(item[1][1]) + '; i++) {')
                            cpp_bufs.append('		len += sprintf(buf + len, "%llu", p->' + item[0] + '[i]);')
                            cpp_bufs.append('	}')
                            cpp_bufs.append('	len += sprintf(buf + len, "\\n");')
                        elif item_type in ('float', 'double'):
                            cpp_bufs.append('	len += sprintf(buf + len, "%s' + item[0] + 's:", prefix);')
                            cpp_bufs.append('	for (int i=0; i<' + str(item[1][1]) + '; i++) {')
                            cpp_bufs.append('		len += sprintf(buf + len, "%f", p->' + item[0] + '[i]);')
                            cpp_bufs.append('	}')
                            cpp_bufs.append('	len += sprintf(buf + len, "\\n");')
                    else:
                        if item_type in ('char', 'unsigned char'):
                            cpp_bufs.append('	len += sprintf(buf + len, "%s%-' + str(struct_item_name_length[struct_name]) + 's: %d\\n", prefix, "' + item[0] + '", p->' + item[0] + ');')
                        elif item_type == 'bool':
                            cpp_bufs.append('	len += sprintf(buf + len, "%s%-' + str(struct_item_name_length[struct_name]) + 's: %s\\n", prefix, "' + item[0] + '", p->' + item[0] + ' ? "True" : "False");')
                        elif item_type in ('int8_t', 'int16_t', 'int32_t'):
                            cpp_bufs.append('	len += sprintf(buf + len, "%s%-' + str(struct_item_name_length[struct_name]) + 's: %d\\n", prefix, "' + item[0] + '", p->' + item[0] + ');')
                        elif item_type in ('uint8_t', 'uint16_t', 'uint32_t'):
                            cpp_bufs.append('	len += sprintf(buf + len, "%s%-' + str(struct_item_name_length[struct_name]) + 's: %u\\n", prefix, "' + item[0] + '", p->' + item[0] + ');')
                        elif item_type == 'int64_t':
                            cpp_bufs.append('	len += sprintf(buf + len, "%s%-' + str(struct_item_name_length[struct_name]) + 's: %lld\\n", prefix, "' + item[0] + '", p->' + item[0] + ');')
                        elif item_type == 'uint64_t':
                            cpp_bufs.append('	len += sprintf(buf + len, "%s%-' + str(struct_item_name_length[struct_name]) + 's: %llu\\n", prefix, "' + item[0] + '", p->' + item[0] + ');')
                        elif item_type in ('float', 'double'):
                            cpp_bufs.append('	len += sprintf(buf + len, "%s%-' + str(struct_item_name_length[struct_name]) + 's: %f\\n", prefix, "' + item[0] + '", p->' + item[0] + ');')

                cpp_bufs.append('	return len;')
                cpp_bufs.append('}\n')
            hdr.write('\n'.join(hdr_bufs))
            cpp.write('\n'.join(cpp_bufs))

            hdr.write('''
};

#endif
''')
