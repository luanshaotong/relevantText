#coding=utf-8

import bsddb

import configuration

import re

if __name__ == '__main__':
    #os.remove(configuration.modelpath+'abs.db')
    abshash = bsddb.hashopen(configuration.modelpath+'abs.db','c')
    file = open(configuration.modelpath+'abs')
    ct = 0
    while True:  
        line = file.readline()
        if not line:  
            break 
        line = line.split(':::')
        piece = {}
        piece['url'] = 'https://scholar.google.com/scholar?q='+line[0]
        piece['title'] = line[0]
        piece['description'] = line[1].lower()
        
        proccessedtitle = line[0].replace('+','\+').replace('(','\(').replace(')','\)').replace('[','\[').replace(']','\]').replace('{','\{').replace('}','\}').replace('|','\|').lower()
        p1 = r"\d+,"+proccessedtitle+",\d+,"+proccessedtitle+",(.+)$"
        p2 = r"\d+,"+proccessedtitle+",\d+,(.+)$"
        p3 = r""+proccessedtitle+"[, | ](.+)$"
        p4 = r",\d+,(.+)$"
        
        pattern1 = re.compile(p1)
        pattern2 = re.compile(p2)
        pattern3 = re.compile(p3)
        pattern4 = re.compile(p4)
        
        if ct <16974:
            match = re.search(pattern1,piece['description'])
            if match is not None:
                piece['description'] = match.group(1)
            else :
                match = re.search(pattern2,piece['description'])
                if match is not None:
                    piece['description'] = match.group(1)
                else :
                    match = re.search(pattern4,piece['description'])
                    #if match is not None:
                    piece['description'] = match.group(1)
        else :
            match = re.search(pattern3,piece['description'])
            if match is not None:
                piece['description'] = match.group(1)
                
        if piece['description'] == None:
            raise 1
        #print piece['description']

        piece['rel'] = False
        abshash[str(ct)] = str(piece)
        ct += 1