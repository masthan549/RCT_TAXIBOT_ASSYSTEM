"""
M file parser for cc settings.

"""
import re
import pprint

def readM(filename):
    """
    Read the MDL file in ASCII and return the data.
    """
    filehandle = open(filename,'r')
    data = filehandle.readlines()
    filehandle.close()
    return data

def ParseMfile(Mdata):
    rDict = {}
    for index in Mdata:
        Mlineparse = re.match('cs.set_param(.*);',index)
        if Mlineparse != None:
            bracestrng = Mlineparse.group(1)
            dictkey = bracestrng.split("'")[1]
            TestStr = re.sub(r'\s','',bracestrng.split("'")[2])
            if TestStr == ',':
                rDict[dictkey] = bracestrng.split("'")[3]
            elif TestStr == ',struct(' or TestStr == ',{':
                tlist = list(set(bracestrng.split("'")[3:-1]))
                tlist.remove(",")
                rDict[dictkey] = tlist
            else:
                rDict[dictkey] = int(bracestrng.split("'")[2].split(")")[0].split(",")[1].strip())
    return rDict
