import numpy as np

from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, \
    Plot, Matrix, Alignat, NoEscape, Command
from pylatex.utils import italic, bold
import os

import re


def unrepr(text):
    "reverse of repr"
    return eval(text)


def hexint(text):
    "converts 0x... hexa string to integer"
    return int(text, 16)


class Parser:
    def __call__(self, data, pattern):
        regexp, types = self.compile(pattern)
        match = regexp.match(data)
        if not match:
            raise ValueError
        groups = [data[match.start("Grp%s" % i):match.end("Grp%s" % i)]
                  for i in range(len(types))]
        return tuple(t(g) for t, g in zip(types, groups))

    def compile(self, pattern):
        chars = []
        types = []
        i = 0
        while i < len(pattern):
            if pattern[i] != "%":
                chars.append(pattern[i])
                i += 1
            elif pattern[i+1] == "%":
                chars.append("%")
                i += 2
            elif pattern[i+1] == "s":
                chars.append("(?P<Grp%s>.*?)" % len(types))
                types.append(str)
                i += 2
            elif pattern[i+1] == "r":
                chars.append("(?P<Grp%s>(?P<Par%s>['\"]).*?(?P=Par%s))"
                             % (len(types), len(types), len(types)))
                types.append(unrepr)
                i += 2
            elif pattern[i+1] == "c":
                chars.append("(?P<Grp%s>.)" % len(types))
                types.append(str)
                i += 2
            elif pattern[i+1] == "u":
                chars.append("(?P<Grp%s>[0-9]+)" % len(types))
                types.append(int)
                i += 2
            elif pattern[i+1] in "di":
                chars.append("(?P<Grp%s>[+-]?[0-9]+)" % len(types))
                types.append(int)
                i += 2
            elif pattern[i+1] in "fF":
                chars.append("(?P<Grp%s>[+-]?[0-9]*\.[0-9]*)" % len(types))
                types.append(float)
                i += 2
            elif pattern[i+1] in "xX":
                chars.append("(?P<Grp%s>0[xX]?[0-9A-Fa-f]*)" % len(types))
                types.append(hexint)
                i += 2
            else:
                raise ValueError
        return re.compile("^" + "".join(chars) + "$"), types


if __name__ == '__main__':
    doc_filename = os.path.join(os.path.dirname(__file__), 'document.texs')

    doc = Document(document_options='titlepage')

    with open(doc_filename, 'r') as reader:
        doc_lines = reader.readlines()

    p = Parser()

    for i in range(0, len(doc_lines)):
        if "\\T " in doc_lines[i]:
            doc_lines[i] = doc_lines[i].replace('\n', '')
            doc.preamble.append(
                Command('title', doc_lines[i].replace('\\T ', '')))
        if "\\A " in doc_lines[i]:
            doc_lines[i] = doc_lines[i].replace('\n', '')
            doc.preamble.append(
                Command('author', doc_lines[i].replace('\\A ', '')))
        if "\\D " in doc_lines[i]:
            doc_lines[i] = doc_lines[i].replace('\n', '')
            if 'today' in doc_lines[i].replace('\\D ', ''):
                doc.preamble.append(Command('date', NoEscape(r'\today')))
            else:
                doc.preamble.append(
                    Command('date', doc_lines[i].replace('\\D ', '')))
        if "\\Make" in doc_lines[i]:
            doc.append(NoEscape(r'\maketitle'))
        if "\\S " in doc_lines[i]:
            doc_lines[i] = doc_lines[i].replace('\n', '')
            with doc.create(Section(doc_lines[i].replace('\\S ', ''))):
                doc.append('')
        elif "\\Ss " in doc_lines[i]:
            doc_lines[i] = doc_lines[i].replace('\n', '')
            with doc.create(Subsection(doc_lines[i].replace('\\Ss ', ''))):
                doc.append('')
        if ('i{' in doc_lines[i]) | ('b{' in doc_lines[i]):
            line = doc_lines[i]
            escape_new = True
            if '\\en' in line:
                line = line.replace('\\en', '')
                escape_new = False
            ital = re.findall(r'i\{.*?\}|b\{.*?\}', line)
            fital = []
            query = '%s'
            for it in ital:
                if('i{' in it):
                    query += 'i{.*}%s'
                    fital.append(p(it, 'i{%s}'))
                else:
                    query += 'b{.*}%s'
                    fital.append(p(it, 'b{%s}'))
            plain_text = p(line, query)
            for i in range(0, fital.__len__()):
                doc.append(plain_text.__getitem__(i))
                if 'i{' in ital.__getitem__(i):
                    doc.append(italic(fital[i].__getitem__(0)))
                else:
                    doc.append(bold(fital[i].__getitem__(0)))
                if plain_text.__getitem__(i+1)[0] == " ":
                    doc.append(NoEscape(r'\hspace{1pt} '))
            doc.append(plain_text.__getitem__(fital.__len__()))
            if escape_new:
                doc.append('\n')

        if ('\\m' in doc_lines[i]):
            doc_lines[i] = doc_lines[i].replace('\\m ', '')
            d = doc_lines[i].split(' ')
            doc.append(Math(data=d))

        if ('\\Mm' in doc_lines[i]):
            doc_lines[i] = doc_lines[i].replace('\n', '')
            doc_lines[i] = doc_lines[i].replace('\\Mm ', '')
            d = doc_lines[i].split(' ')
            M1 = str(d.__getitem__(0))
            M2 = str(d.__getitem__(1))
            M1 = M1.split(';')
            M2 = M2.split(';')
            for i in range(0, M1.__len__()):
                M1[i] = M1[i].split(',')
            for i in range(0, M2.__len__()):
                M2[i] = M2[i].split(',')
            a = np.matrix(M1, dtype=float)
            b = np.matrix(M2, dtype=float)
            doc.append(Math(data=[Matrix(a), Matrix(b), '=', Matrix(a * b)]))

    print(doc_lines)

    with doc.create(Subsection('Table of something')):
        with doc.create(Tabular('rc|cl')) as table:
            table.add_hline()
            table.add_row((1, 2, 3, 4))
            table.add_hline(1, 2)
            table.add_empty_row()
            table.add_row((4, 5, 6, 7))

    with doc.create(Section('The fancy stuff')):
        with doc.create(Subsection('Beautiful graphs')):
            with doc.create(TikZ()):
                plot_options = 'height=4cm, width=6cm, grid=major'
                with doc.create(Axis(options=plot_options)) as plot:
                    plot.append(Plot(name='model', func='-x^5 - 242'))

                    coordinates = [
                        (-4.77778, 2027.60977),
                        (-3.55556, 347.84069),
                        (-2.33333, 22.58953),
                        (-1.11111, -493.50066),
                        (0.11111, 46.66082),
                        (1.33333, -205.56286),
                        (2.55556, -341.40638),
                        (3.77778, -1169.24780),
                        (5.00000, -3269.56775),
                    ]

                    plot.append(Plot(name='estimate', coordinates=coordinates))

    doc.generate_pdf('full', clean_tex=False)
