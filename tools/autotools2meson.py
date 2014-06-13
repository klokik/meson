#!/usr/bin/python3

# Copyright 2014 Jussi Pakkanen

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import sys, os

class Converter():
    def __init__(self, root):
        self.project_root = root

    def readlines(self, file):
        line = file.readline()
        while line != '':
            line = line.rstrip()
            while line.endswith('\\'):
                line = line[:-1] + file.readline().rstrip()
            yield line
            line = file.readline()

    def convert(self, subdir=None):
        if subdir is None:
            subdir = self.project_root
        try:
            ifile = open(os.path.join(subdir, 'Makefile.am'))
        except FileNotFoundError:
            print('Makefile.am not found in subdir', subdir)
        ofile = open(os.path.join(subdir, 'meson.build'), 'w')
        for line in self.readlines(ifile):
            items = line.strip().split()
            if len(items) == 0:
                ofile.write('\n')
                continue
            if items[0] == 'SUBDIRS':
                for i in items[2:]:
                    if i != '.':
                        ofile.write("subdir('%s')\n" % i)
                        self.convert(os.path.join(subdir, i))
            elif items[0].endswith('_SOURCES'):
                self.convert_target(ofile, items)
            else:
                ofile.write("# %s\n" % line)

    def convert_target(self, ofile, items):
        if items[0].endswith('la_SOURCES'):
            func = 'shared_library'
            tname = "'%s'" % items[0][:-11]
        else:
            func = 'executable'
            tname = "'%s'" % items[0][:-8]
        sources = [tname]
        for s in items[2:]:
            if s.startswith('$('):
                s = s[2:-1]
            elif s.startswith('$'):
                s = s[1:]
            else:
                s = "'%s'" % s
            sources.append(s)
        ofile.write('%s(%s)\n' % (func, ',\n'.join(sources)))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(sys.argv[0], '<Autotools project root>')
        sys.exit(1)
    c = Converter(sys.argv[1])
    c.convert()
