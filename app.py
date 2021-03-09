import numpy as np
from myParser import Parser
from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, \
    Plot, Matrix, Alignat, NoEscape, Command
from pylatex.utils import italic, bold
import os
import re


if __name__ == '__main__':
    doc_filename = os.path.join(os.path.dirname(__file__), 'document.texs')

    with open(doc_filename, 'r') as reader:
        doc_lines = reader.readlines()

    if ('\\2col' in doc_lines[0]) & ('\\Title' in doc_lines[0]):
        doc = Document(document_options='titlepage, twocolumn')
    elif '\\2col' in doc_lines[0]:
        doc = Document(document_options='twocolumn')
    elif '\\Title' in doc_lines[0]:
        doc = Document(document_options='titlepage')
    else:
        doc = Document()

    p = Parser()
    tex_present = False

    for i in range(1, len(doc_lines)):

        if '// ' in doc_lines[i]:
            comment_split = doc_lines[i].split('// ')
            doc_lines[i] = comment_split[0]

        if "\\T " in doc_lines[i]:
            doc_lines[i] = doc_lines[i].replace('\n', '')
            doc.preamble.append(
                Command('title', doc_lines[i].replace('\\T ', '')))

        elif "\\A " in doc_lines[i]:
            doc_lines[i] = doc_lines[i].replace('\n', '')
            doc.preamble.append(
                Command('author', doc_lines[i].replace('\\A ', '')))

        elif "\\D " in doc_lines[i]:
            doc_lines[i] = doc_lines[i].replace('\n', '')
            if 'today' in doc_lines[i].replace('\\D ', ''):
                doc.preamble.append(Command('date', NoEscape(r'\today')))
            else:
                doc.preamble.append(
                    Command('date', doc_lines[i].replace('\\D ', '')))

        elif "\\Make" in doc_lines[i]:
            doc.append(NoEscape(r'\maketitle'))

        elif "\\S " in doc_lines[i]:
            doc_lines[i] = doc_lines[i].replace('\n', '')
            with doc.create(Section(doc_lines[i].replace('\\S ', ''))):
                doc.append('')

        elif "\\Ss " in doc_lines[i]:
            doc_lines[i] = doc_lines[i].replace('\n', '')
            with doc.create(Subsection(doc_lines[i].replace('\\Ss ', ''))):
                doc.append('')

        elif ('i{' in doc_lines[i]) | ('b{' in doc_lines[i]):
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

        elif ('\\m ' in doc_lines[i]):
            doc_lines[i] = doc_lines[i].replace('\\m ', '')
            d = doc_lines[i].split(' ')
            doc.append(Math(data=d))

        elif ('im{' in doc_lines[i]):
            line = doc_lines[i]
            ital = re.findall(r'im\{.*?\}', line)
            fital = []
            query = '%s'
            for it in ital:
                query += 'im{.*}%s'
                fital.append(p(it, 'im{%s}'))
            plain_text = p(line, query)
            for i in range(0, fital.__len__()):
                doc.append(plain_text.__getitem__(i))
                doc.append(Math(data=fital.__getitem__(i)[0], inline=True))
                if plain_text.__getitem__(i+1)[0] == " ":
                    doc.append(NoEscape(r'\hspace{1pt} '))
            doc.append(plain_text.__getitem__(fital.__len__()))

        elif ('\\Mmi ' in doc_lines[i]):
            doc_lines[i] = doc_lines[i].replace('\n', '')
            doc_lines[i] = doc_lines[i].replace('\\Mmi ', '')
            d = doc_lines[i].split(' ')
            M1 = str(d.__getitem__(0))
            M2 = str(d.__getitem__(1))
            M1 = M1.split(';')
            M2 = M2.split(';')
            for i in range(0, M1.__len__()):
                M1[i] = M1[i].split(',')
            for i in range(0, M2.__len__()):
                M2[i] = M2[i].split(',')
            a = np.matrix(M1, dtype=int)
            b = np.matrix(M2, dtype=int)
            doc.append(
                Math(data=[Matrix(a), Matrix(b), '=', Matrix(a * b)], inline=True))

        elif ('\\Mmf ' in doc_lines[i]):
            doc_lines[i] = doc_lines[i].replace('\n', '')
            doc_lines[i] = doc_lines[i].replace('\\Mmf ', '')
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
            doc.append(
                Math(data=[Matrix(a), Matrix(b), '=', Matrix(a * b)], inline=True))

        elif '\\Tab ' in doc_lines[i]:
            doc_lines[i] = doc_lines[i].replace('\n', '')
            doc_lines[i] = doc_lines[i].replace('\\Tab ', '')
            prop = doc_lines[i].split(' ')
            with doc.create(Tabular(prop[0])) as table:
                for i in range(1, prop.__len__()):
                    if prop.__getitem__(i) == '\\h':
                        table.add_hline()
                    elif '\\h(' in prop.__getitem__(i):
                        prop1 = prop.__getitem__(i).replace('\\h(', '')
                        prop2 = prop1.replace(')', '')
                        prop3 = prop2.split(',')
                        table.add_hline(prop3[0], prop3[1])
                    elif '\\e' == prop.__getitem__(i):
                        table.add_empty_row()
                    else:
                        prop1 = prop.__getitem__(i).split(',')
                        table.add_row(prop1)

        elif '\\Center' in doc_lines[i]:
            doc.append(NoEscape(r'\begin{center}'))

        elif '\\Ecenter' in doc_lines[i]:
            doc.append(NoEscape(r'\end{center}'))

        elif ('\\Tex{' in doc_lines[i]) | tex_present:
            if not tex_present:
                doc_lines[i] = doc_lines[i].replace('\\Tex{', '')
            if ' }' in doc_lines[i]:
                tex_present = False
                doc_lines[i] = doc_lines[i].replace(' }', '')
                doc.append(NoEscape(doc_lines[i]))
            else:
                tex_present = True
                doc.append(NoEscape(doc_lines[i]))

        else:
            if doc_lines[i] == '\n':
                doc_lines[i] = doc_lines[i].replace('\n', '')
            doc.append(doc_lines[i])

    with doc.create(Section('The fancy stuff')):
        with doc.create(Subsection('Beautiful graphs')):
            with doc.create(TikZ()):
                plot_options = 'height=4cm, width=6cm, grid=minor'
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
