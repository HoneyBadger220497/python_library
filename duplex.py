#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 16:19:07 2019

@author: philippschreiner
"""

import os
import sys
from PyPDF2 import PdfFileReader, PdfFileWriter

def duplex():
    files = sys.argv[1:]
    path = os.getcwd()
    front = PdfFileReader(path + '/' + files[0])
    back = PdfFileReader(path + '/' + files[1])
    numPages = front.getNumPages()
    stack = PdfFileWriter()

    for page in range(numPages):
        stack.addPage(front.getPage(page))
        stack.addPage(back.getPage(-page-1))

    with open(path + '/stack.pdf','wb') as output:
        stack.write(output)

if __name__ == '__main__':
    sys.exit(duplex())
