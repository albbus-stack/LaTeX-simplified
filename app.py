import numpy as np

from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, \
    Plot, Matrix, Alignat, NoEscape
from pylatex.utils import italic, bold
import os

if __name__ == '__main__':
    doc_filename = os.path.join(os.path.dirname(__file__), 'document.texs')

    geometry_options = {"tmargin": "1cm", "lmargin": "1cm"}

    doc = Document(geometry_options=geometry_options)

    with open(doc_filename, 'r') as reader:
        doc_lines = reader.readlines()

    for i in range(0, len(doc_lines)):
        if "\\S " in doc_lines[i]:
            doc_lines[i] = doc_lines[i].replace('\n', '')
            with doc.create(Section(doc_lines[i].replace('\\S ', ''))):
                doc.append('')
        elif "\\Ss " in doc_lines[i]:
            doc_lines[i] = doc_lines[i].replace('\n', '')
            with doc.create(Subsection(doc_lines[i].replace('\\Ss ', ''))):
                doc.append('')
        elif 'i{' in doc_lines[i]:
            line = doc_lines[i]
            final = ' '
            ital = ''
            start = ''
            j = 0
            k = len(line)
            while j < len(line)-1:
                if (line[j] == 'i') & (line[j+1] == '{'):
                    k = j+2
                    while line[j+2] != '}':
                        ital += line[j+2]
                        j = j+1
                    j = j+3
                if j <= k:
                    start += line[j]
                else:
                    final += line[j]
                j = j+1
            final += line[j]
            doc.append(start)
            doc.append(italic(ital))
            doc.append(NoEscape(r'\hspace{1pt} '))
            doc.append(final)
        elif 'b{' in doc_lines[i]:
            line = doc_lines[i]
            final = ' '
            bol = ''
            start = ''
            j = 0
            k = len(line)
            while j < len(line)-1:
                if (line[j] == 'b') & (line[j+1] == '{'):
                    k = j+2
                    while line[j+2] != '}':
                        bol += line[j+2]
                        j = j+1
                    j = j+3
                if j <= k:
                    start += line[j]
                else:
                    final += line[j]
                j = j+1
            final += line[j]
            doc.append(start)
            doc.append(bold(bol))
            doc.append(NoEscape(r'\hspace{1pt} '))
            doc.append(final)

    print(doc_lines)

    with doc.create(Section('The simple stuff')):
        doc.append('Some regular text and some ')
        doc.append(italic('italic text.'))
        doc.append('\nAlso some crazy characters: $&#{}')
        with doc.create(Subsection('Math that is incorrect')):
            doc.append(Math(data=['2*3', '=', 9]))

        with doc.create(Subsection('Table of something')):
            with doc.create(Tabular('rc|cl')) as table:
                table.add_hline()
                table.add_row((1, 2, 3, 4))
                table.add_hline(1, 2)
                table.add_empty_row()
                table.add_row((4, 5, 6, 7))

    a = np.array([[100, 10, 20]]).T
    M = np.matrix([[2, 3, 4],
                   [0, 0, 1],
                   [0, 0, 2]])

    with doc.create(Section('The fancy stuff')):
        with doc.create(Subsection('Correct matrix equations')):
            doc.append(Math(data=[Matrix(M), Matrix(a), '=', Matrix(M * a)]))

        with doc.create(Subsection('Alignat math environment')):
            with doc.create(Alignat(numbering=False, escape=False)) as agn:
                agn.append(r'\frac{a}{b} &= 0 \\')
                agn.extend([Matrix(M), Matrix(a), '&=', Matrix(M * a)])

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
