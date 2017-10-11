#coding=utf-8
'''
Created on 2017��1��19��

@author: luan
'''

import sys
import urllib

def quote(str):
    if sys.version_info.major==3:
        return urllib.parse.quote_plus(str)
    else:
        return urllib.quote_plus(str)
    
def unquote(str):
    if sys.version_info.major==3:
        return urllib.parse.unquote_plus(str)
    else:
        return urllib.unquote_plus(str)
     