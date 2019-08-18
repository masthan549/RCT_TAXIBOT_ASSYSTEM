#!/usr/bin/env python
from pyparsing import *
import re
import string
import os,sys

if __name__ == '__main__':
    argv ="'matshan vali \n syed','lalubu'"
    afterremovingLines=re.match(r'(.*)',argv,re.MULTILINE)	
    print afterremovingLines.group()