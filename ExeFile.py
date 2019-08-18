#import os
import fileinput
import re
import RuleCheckerAPI_WoGUI
import thread
import sys
import os.path

class RuleChecker:
    '''
	Documentation
    '''
    def __init__(self,Arguments):
 	
        self.FilePathDict = {}
        self.DependList = []
        self.selecteditem = ''
        self.fileNames = [] 		

        #self.__searchFilesAndUpdateList()
        self.validateInputArguments(Arguments)
		
    def validateInputArguments(self,Arg):	

    	#command line arguments should be two
        # MDLFilesLocation=Arg[1:len(Arg)]	
        # if len(MDLFilesLocation)>1:
            # MDLFilesLocation=' '.join(MDLFilesLocation)
        # #print MDLFilesLocation[0]
        # PathLocation=MDLFilesLocation[0]		
        PathLocation=raw_input('\n\n Enter MDL files path:')		
        if os.path.exists(PathLocation) == True:		
            #Search For all MDL file in given Directory
            self.__searchFilesAndUpdateList(PathLocation)
			
            #Throw error If selected path have Redundent Files
            self.__checkDuplicatesInList()			
            
            #print the List of .mdl files in given location
            if len(self.fileNames)==0:
                print 'selected path has no .mdl file!!'
                sys.exit()
 
            print '\n\nModel Files in Selected directory are:\n'
            for mdlIndex in self.fileNames:			
                print mdlIndex                       
				
            self.selecteditem=raw_input('\n\nSelect the Model File Name:')
            if self.selecteditem in self.fileNames: 			
                self.__checkDependency(self.selecteditem) 
                self.DependList.append(self.selecteditem)
                RuleCheckerAPI_WoGUI.RuleCheck(self.DependList, self.FilePathDict, self.selecteditem)
            else:
                print '\nselected file is not exist in given path!!' 			
                sys.exit()
				
        else:
            print 'Please Enter valid path!!' 			
            sys.exit() 			
			
    def __searchFilesAndUpdateList(self,MDLfilesDir):
        self.FilePathDict = {}
        self.fileNames = []		
        for root, dirs, files in os.walk(MDLfilesDir):
          for file in files:
            if file.endswith('.mdl'):
                self.FilePathDict[str(file[:-4])] = str(os.path.join(root, file))
                self.fileNames.append(file[:-4])				

    def __checkDuplicatesInList(self):
        templist = []
        for index in range(len(self.fileNames)):
            templist.append(self.fileNames[index])
        templistlen = len(templist)
        tempsetlen = len(list(set(templist)))
        if templistlen != tempsetlen:
            print "\n\nSelected Path has duplicate mdl files, Please select the folder having unique files!!"
            sys.exit()
				
    def __checkDependency(self, selection):
        checkDepLc = []
        FilePath = ''
        try:
            FilePath = self.FilePathDict[selection]
        except KeyError:
            self.DependList.remove(selection)
        if FilePath != '':
            for fline in fileinput.input(self.FilePathDict[selection]):
                if "ModelRefBlockPath" in fline:
                    checkDep = (re.split('[/|]', fline.split('"')[1]))
                    checkDepLc = list(set([x for x in checkDep]))
                    try:
                        checkDepLc.remove(selection)
                    except ValueError:
                        pass
                    self.DependList += checkDepLc
                if "SourceBlock" in fline:
                    checkDep = (re.split('[/]', fline.split('"')[1]))
                    if len(checkDep) == 2:
                        if checkDep[-1] not in ['Model Info', 'DocBlock', 'Function-Call\\nGenerator']:
                            self.DependList.append(checkDep[0])
                            checkDepLc.append(checkDep[0])
            fileinput.close()
            for selx in checkDepLc:    # recursive
                self.__checkDependency(selx)
            #This Exception pass even If you don't have Dependency Model					
if __name__ == '__main__':
    ruleCheckObj = RuleChecker(sys.argv)
		
