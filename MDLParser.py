"""
file parser.

"""
import re
from pyparsing import *
import pprint

# parse actions
def convertNumbers(s,l,toks):
    """
    Convert tokens to int or float
    """
    n = toks[0]
    try:
        return int(n)
    except ValueError:
        return float(n)

def joinStrings(s,l,toks):
    """
    Join string split over multiple lines
    """
    return ["".join(toks)]
    

def readMDL(filename):
    """
    Read the MDL file in ASCII and return the data.
    """
    filehandle = open(filename,'r')
    data = filehandle.read()
    filehandle.close()
    return data

#def writeParseData(data):
#    """
#    Write the parsed data from MDL into a file
#    """
#    filehandle = open(".\Output.txt",'w')
#    filehandle.write(str(data))
#    filehandle.close()


def MDLParserSettings():
    """
     Parse double quoted strings. Ideally we should have used the simple statement:
        dblString = dblQuotedString.setParseAction( removeQuotes )
     Unfortunately dblQuotedString does not handle special chars like \n \t,
     so we have to use a custom regex instead.
    """
    # Regular expression to fetch string.
    dblString = Regex(r'\"(?:\\\"|\\\\|[^"])*\"', re.MULTILINE)
    dblString.setParseAction( removeQuotes )

    # Expressen to extract number.
    mdlNumber = Combine( Optional('-') + ( '0' | Word('123456789',nums) ) +
                        Optional( '.' + Word(nums) ) +
                        Optional( Word('eE',exact=1) + Word(nums+'+-',nums) ) )

    #print "mdlNumber"
    #pprint.pprint(mdlNumber)
    
    mdlObject = Forward()
    mdlName = Word('$'+'.'+'_'+alphas+nums)
    #print "mdlName"
    #pprint.pprint(mdlName)


    mdlValue = Forward()
    # Strings can be split over multiple lines
    mdlString = (dblString + Optional(OneOrMore(Suppress(LineEnd()) + LineStart()
                 + dblString)))

    #print "mdlString"
    #pprint.pprint(mdlString)

    mdlElements = delimitedList( mdlValue )

    #print "mdlElements"
    #pprint.pprint(mdlElements)

    mdlArray = Group(Suppress('[') + Optional(mdlElements) + Suppress(']') )

    #print "mdlArray"
    #pprint.pprint(mdlArray)
    
    mdlMatrix =Group(Suppress('[') + (delimitedList(Group(mdlElements),';')) \
                  + Suppress(']') )

    #print "mdlMatrix"
    #pprint.pprint(mdlMatrix)

    mdlValue << ( mdlNumber | mdlName| mdlString  | mdlArray | mdlMatrix )

    #print "mdlValue"
    #pprint.pprint(mdlValue)

    memberDef = Group( mdlName  + mdlValue ) | Group(mdlObject)

    #print "memberDef"
    #pprint.pprint(memberDef)
    
    mdlMembers = OneOrMore( memberDef)

    #print "mdlMembers"
    #pprint.pprint(mdlMembers)
    
    # MDL parse will be output in the form of Dict
    #mdlObject << ( mdlName+Dict(Suppress('{') + Optional(mdlMembers) + Suppress('}')) )

    # MDL parse will be output in the form of list
    mdlObject << ( mdlName+Suppress('{') + Optional(mdlMembers) + Suppress('}') )

    #print "mdlObject"
    #pprint.pprint(mdlObject)
    
    mdlNumber.setParseAction( convertNumbers )
    mdlString.setParseAction(joinStrings)

    # Ignore all lines that start with a #
    singleLineComment = Group("#" + restOfLine)
    mdlObject.ignore(singleLineComment)
    return mdlObject


