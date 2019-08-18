#Standard
import pprint # debug purpose

#Local
from MDLParser import *
from MParser import *
import DataDictionary
import DataLogger_WoGUI
import os
import copy
import re
import sys

# Global variables
MISRACheckbox = True
Hi_intCheckbox = True
RICARDOCheckbox = True

CancelRuleCheck = False

#______________________________________________________________________________________________
#______________________________________________________________________________________________
#______________________________________________________________________________________________

def RuleCheck(DependList, FilePathDict, SelectedItem):
    mdlparser = MDLParserSettings()
   
    
    filePathLocation = FilePathDict[SelectedItem]
    afterSplit=filePathLocation.split('\\')
    afterSplit=afterSplit[0:len(afterSplit)-1]
    filelocation='\\'.join(afterSplit) 	
    #Log file for storing the ERROR Result
    filePtr = open(filelocation+'\\'+SelectedItem+'_log.txt','w') 	
    dataLoggerObj = DataLogger_WoGUI.DataLogger(SelectedItem, filePtr,filelocation)
    Modules = {}

    for DependLstitem in DependList:
        if CancelRuleCheck == False:#Remove this code later
            if DependLstitem in FilePathDict:
                testdata = readMDL(FilePathDict[DependLstitem])
                resultMD = mdlparser.parseString(testdata)
                resultMD = resultMD.asList()
                # handle stateflow
                stateFlowStart = testdata.rfind('Stateflow {')
                resultSF = []
                if stateFlowStart != -1:
                    #replace the [ (when [ preceded by tab or space) with "[
                    resultRefinedSF = testdata[stateFlowStart:].replace('	[','"[')
                    resultRefinedSF = testdata[stateFlowStart:].replace(' [','"[')
                    #replace the ] (when ] followed by newLine) with ]"
                    resultRefinedSF = resultRefinedSF.replace((']'+'\n'),']"')
                    resultRefinedSF = resultRefinedSF.replace('""[','"[')
                    resultRefinedSF = resultRefinedSF.replace(']""',']"')
                    resultSF = mdlparser.parseString(resultRefinedSF)
                    resultSF = resultSF.asList()
                Modules[DependLstitem] = RuleChecker(dataLoggerObj, resultMD, resultSF, DependLstitem)
                Modules[DependLstitem].processAllRulesC()
            else:
                filePtr.writelines('ERROR    >>>  Dependancy file \"'+DependLstitem+'\" does not exist to process the rule \n')

    if CancelRuleCheck == False:
        
        filePtr.writelines('\n===============================================================================')		
        if dataLoggerObj.RuleCheckFailed == 1:
            filePtr.writelines('\nRESULT    >>>  FAILED\nRule check details are recorded in >>> '+\
			                    filelocation +'\\'+ SelectedItem+'_Man.csv')
        elif dataLoggerObj.RuleCheckFailed == 2:
            filePtr.writelines('\nRESULT    >>>  NEEDS MANUAL CHECK\nRule check details are recorded in >>> '+\
			                    filelocation +'\\'+ SelectedItem+'_Man.csv\n')
        else:
            filePtr.writelines('\nRESULT    >>>  PASS\nRule check details are recorded in >>> '+\
			                    filelocation +'\\'+ SelectedItem+'_Man.csv\n')
        filePtr.writelines('\n===============================================================================')		
        filePtr.close()		
        print '\n\nRule check is completed Successfully!!\n'
        print '\nCheck the results in:\n'+filelocation+'\\'+SelectedItem+'_log.txt'
        sys.exit()		
    else:#Remove this code later
        print 'Rule Check is Cancelled'
        sys.exit()		
#______________________________________________________________________________________________
#______________________________________________________________________________________________
#______________________________________________________________________________________________

class RuleChecker(object):

    def __init__(self, LoggerObj, MDinlist, SFinlist, ModUndRev):
        #If Model diagram Line has any Branches,then separate such data into individual Line data 	
        MDinlist2=self.lineDataModify(MDinlist)
        self.__MDLlist = MDinlist2
        self.__SFlist = SFinlist
        self.dataLoggerObj = LoggerObj
        self.ModuleName = ModUndRev
        self.__SystemBlock = []
        self.__DefaultBlkParm = []
        self.SubSysData = []
        self.IndividualSystemData=[]
        self.NotNamedBusSignal = []
        self.BusCreatorOutputSignalName = []
        self.BusCreatorInputSignalName = []
        self.NotNamedOutputBuscreatorSignals = []
        self.NotNamedInputBusCreatorSignals = []
        self.BusSignals = []
        self.deMuxInputSignalNames	= []
        self.mutualState = []
        self.BoolPrtyData = {}
        self.noOfSubsystems = 0
        self.subsystemCntr = 0
        self.storeSysBlckAndDefaultBlckParm(self.__MDLlist)
        self.buildSubSystemData()

    #______________________________________________________________________________________________
    # Fetches the position of an item from the input list and returns the list of positions
    # in terms of a tuple.
    def _getItemPosition(self, xs, item):
        if isinstance(xs, list):
            for i, it in enumerate(xs):
                for pos in self._getItemPosition(it, item):
                    yield (i,) + pos
        elif xs == item:
            yield ()

    #______________________________________________________________________________________________
    def lineDataModify(self,mdlData):
        '''
           When you connect Line as a Branch in Model Diagram,Inside the Line Properties
		   in .mdl file we can see Branch Block.So to removing such Branch information
           from Line and adding it individually back to Line information we required this 
           utility.
           Procedure:
           ----------
                    Fetch all Line information form .mdl file and search for the Branch 
                    inforamtion inside the Line data.if Line information doesn't have 
					Branch in it increment bCount otherwise take all Branch information into
                    "branchInfo" List and Line data without Branches into "LineData" . 
                    Now append "branchInfo" and "LineData" individually back to "mdfyLineData".					
        '''
        LineInfomodified = False
        MdlData = list(mdlData)
        while(LineInfomodified == False):
            LinePos=list(self._getItemPosition(MdlData, 'Line'))
            #This variable contains the number of Lines which doesn't have Branch information
            #in Line data			
            bCount = 0
            for LineIndex in range(0,len(LinePos)):
                tempLinePos=LinePos[LineIndex]
                #Extract the Line Information				
                LineData = self._getCmpleteBlck(MdlData, tempLinePos)
                #search for 'Branch' information in Line Data                 
                BranchPos=list(self._getItemPosition(LineData, 'Branch'))
                if len(BranchPos)>0:
                    #extract all Branch Information in Line data
                    branchInfo = []
                    #extract Branch information from Line data and add it into branchInfo 					
                    tempVal = 0					
                    for BranchIndex in range(0,len(BranchPos)):
                        if BranchPos[BranchIndex][1] == 0:
                            tempBrnchPos = BranchPos[BranchIndex][0]
                            popedBranchInfo = LineData.pop(tempBrnchPos-tempVal)
                            tempVal = tempVal+1							
                            #remove branch branch name  							
                            branchInfo.append(popedBranchInfo[1:])
                    dLineData=[]
                    mdfyLineData = []
                    #append Individual Branch information to Line information
                    for apIndex in range(0,len(branchInfo)):
                        LineDta = {}
                        dLineData=list(LineData)	
                        for brInex in range(0,len(branchInfo[apIndex])):
                            dLineData.append(branchInfo[apIndex][brInex])
                        LineDta['LineInfo'] = dLineData	
                        mdfyLineData.append(LineDta)						
                        dLineData = []		
						
                    #mdfyLineData contain Line Data
                    #Convert tuple to list
                    posTmpTuple = list(tempLinePos)
                    MData = list(MdlData)
                    CMdlData = list(MdlData)					
                    #Take a copy of the input list
                    tempMdlData = []  					
                    for posindex in posTmpTuple[:-2]:
                        tempDict = {} 					
                        # Update the temp list in every iteration to get into the bottom of the list.
                        MData = MData[posindex]
                        tempDict['data'] = MData
                        tempDict['Pos'] = posindex 	
                        tempMdlData.append(tempDict)						
                    #Remove the Line data which have Branch in it. 						
                    MData.pop(posTmpTuple[len(posTmpTuple)-2:len(posTmpTuple)-1][0])
                    #appened line Information to the mdlFile 
                    for lIndex in range(0,len(mdfyLineData)):
                        lData = mdfyLineData[lIndex]['LineInfo']
                        lData.insert(0,'Line')
                        MData.append(lData)
                    #pop the last Line info data List and insert modified List					
                    tempMdlData.pop()
                    tempDict = {}
                    tempDict['data'] = MData
                    tempDict['Pos'] = posindex 	
                    tempMdlData.append(tempDict)
 
                    tempMdlData.reverse()
                    #append the subLists information back to SystemData 					
                    for indx in range(0,len(tempMdlData)):
                        if (len(tempMdlData)-1)>indx:
                            position  = tempMdlData[indx]['Pos']
                            data =  tempMdlData[indx]['data']
                            Ndata= tempMdlData[indx+1]['data']
                            Ndata.pop(position)
                            Ndata.insert(position,data)
                            tempMdlData[indx+1]['data'] = Ndata
                    CMdlData.pop(tempMdlData[indx]['Pos'])
                    #add SystemData back to MdlData					
                    CMdlData.append(tempMdlData[indx]['data'])
                    MdlData = CMdlData
                    break
                else:
                    bCount = bCount+1
            if bCount == len(LinePos):
                LineInfomodified = True
        return MdlData                    
            		
    #______________________________________________________________________________________________
	
    # Returns the next list in the model
    def _getNextList(self):
        foundLst = True
        returnLst = []
        Name = ''
        if(self.subsystemCntr < self.noOfSubsystems):
            returnLst = self.SubSysData[self.subsystemCntr]
            Name = self.SubSysData[self.subsystemCntr]['Name']
            self.subsystemCntr = self.subsystemCntr + 1
        elif (self.subsystemCntr == self.noOfSubsystems):
            returnLst = self.__SystemBlock[0]
            self.subsystemCntr = self.subsystemCntr + 1
            Name = self.ModuleName
        else:
            foundLst = False
            self.subsystemCntr = 0

        return returnLst, foundLst, Name
    #______________________________________________________________________________________________
    # Fetches the complete block at the requested position from the input list.
    def _getCmpleteBlck(self, inpLst, posLstTuple):
        #Convert tuple to list
        posTmpTuple = list(posLstTuple)
        #Take a copy of the input list
        inpTmpLst = list(inpLst)
        # By-Pass any exception.
        try:
            # Loop through the tuple discarding. The last element is discarded to stay at the
            # upper level. we need the next element position from the upper level.
            for posindex in posTmpTuple[:-1]:
                # Update the temp list in every iteration to get into the bottom of the list.
                inpTmpLst = inpTmpLst[posindex]
        except:
            pass
        # By-Pass any exception.
        try:
            # The first element will be the block name itself. So discard the first element.
            # The remaining will be the complete block.
            inpTmpLst = inpTmpLst[1:]
        except:
            pass
        # return the complete block.
        return inpTmpLst


    #______________________________________________________________________________________________
    # pops/removes the complete block at the requested position from the input list.
    def _popCmpleteBlck(self, inpLst, posLstTuple):
        #Convert tuple to list
        posTmpTuple = list(posLstTuple)

        #Take a copy of the input list
        inpTmpLst = inpLst
        Sublist = []

        if len(posTmpTuple) > 3:

            # By-Pass any exception.
            try:
                # Loop through the tuple discarding. The last element is discarded to stay at the
                # upper level. we need the next element position from the upper level to pop.
                for posindex in posTmpTuple[:-3]:
                    # Update the temp list in every iteration to get into the bottom of the list.
                    inpTmpLst = inpTmpLst[posindex]
            except:
                pass
            Sublist = inpTmpLst.pop(posTmpTuple[-3])
        return Sublist

    #______________________________________________________________________________________________
    # Fetches the value of the requested propety (if available) from any block and returns the property value
    # dictionary.
    def _getGenericBlckPrpty(self, inpLst, propList):
        retGetStats = 0
        retSubLst = []
        retDict = {}
        retGetLst = []
        inpDict = {}
        # Loop through all the elements of the list and check if the list contains any sublist or single element..
        for popindex in range(len(inpLst)-1,-1,-1):
        # When the item is poped, the index will reduce and an error will be raised. Ignore that error.
            #print inpLst,popindex		
            try:
                if len(inpLst[popindex]) != 2:
                    # If the element is a sublist, delete the sublist from the main list.
                    retSubLst.append(inpLst.pop(popindex)[0])
            except IndexError:
                pass
        # Convert the list to dictionary.
        try:
            inpDict = dict(inpLst)
        except:
            pass

        #Check each item in the dictionary for the items in the property.
        for item in propList:
            #If any of the porperty is found in the main list
            if item in inpDict.keys():
                # Note down that property item and the value
                retDict[item] = inpDict[item]
        #If something is found, then the search is found something. So return 1
        if len(retDict) > 0:
            retGetStats = 1
        #Remove any duplicate items in the sublist header
        retSubLst = list(set(retSubLst))
        return retGetStats, retDict, retSubLst
    #-------------------------------------------------------------------------------------------

    def storeSysBlckAndDefaultBlckParm(self, inplist):
        srchBlck = []
        # Find the position of the BlockParameterDefaults in the main list.
        settingPositionlist2 = list(self._getItemPosition(inplist, 'BlockParameterDefaults'))
        #If the position is found then process for the property values.
        if (len(settingPositionlist2)) > 0:
            # Loop through each key position
            for settingPosIndex in settingPositionlist2:
                # Get the complete block for the key postion.
                srchBlck = self._getCmpleteBlck(inplist, settingPosIndex)
                if len(srchBlck) > 1:
                    break
        self.__DefaultBlkParm = srchBlck

        srchBlck = []
        SystemList = []
        # Find the position of the System in the main list.
        settingPositionlist = list(self._getItemPosition(inplist, 'System'))
        #print  len(settingPositionlist)
        #If the position is found then process for the property values.
        #print settingPositionlist
        if (len(settingPositionlist)) > 0:
            # Loop through each key position
            for settingPosIndex in settingPositionlist:
                # Get the complete block for the key postion.
                srchBlck = self._getCmpleteBlck(inplist, settingPosIndex)
                SystemList = self._getCmpleteBlck(inplist, settingPosIndex)
                #print 'one'
                if len(srchBlck) > 1:
                    break

		#removing SubSystem Data from Main System Block

        positionOfSubSystem = list(self._getItemPosition(SystemList, 'SubSystem'))
        #If Model file have any subSystem then add remove and add only MainSystem Data
        if len(positionOfSubSystem)>0:
            position =positionOfSubSystem[0]
            SystemList[position[0]:position[0]+1] = []
            self.IndividualSystemData.append(SystemList)
        else:
		    self.IndividualSystemData.append(SystemList)

        SystemDetail = {}
        SystemDetail['List'] = list(SystemList)

        inpLst = list(SystemDetail['List'])
        LinkData = []
        srchKeys = ['Name','SrcBlock', 'SrcPort', 'DstBlock', 'DstPort']
        LinkData  = self._getSrchDataFromSubBlck_RCAPI(inpLst, 'Line', srchKeys)
        SystemDetail['LinkData'] = list(LinkData)
        self.__SystemBlock.append(SystemDetail)



    #-------------------------------------------------------------------------------------------

    # Decomposes subsystem from the list and builds line data base for each subsytem and fetches the
    # subsystem name and stores in the dictionary of subsystem.

    def buildSubSystemData(self):
        inpLst = list(self.__MDLlist)
        # Get the position of the subsystem
        poslist = list(self._getItemPosition(inpLst, 'System'))
        # Make a copy of the input list.
        inpLstCopy = list(inpLst)

        if len(poslist) > 0 :
            # remove default parameter block postion
            poslist = poslist[1:]
            # reveres the list to pop from bottem up.
            poslist.reverse()
            # Decompose each subsystem in the list.
            for positem in poslist:
                subSystemDetail = {}
                # Decompose the last subsystem from the list.
                retlist = self._popCmpleteBlck(inpLstCopy, positem)

				#append all subSystems Data to IndividualSystemData
                HoldValue = list(retlist)
                self.IndividualSystemData.append(HoldValue)

                subSystemDetail['List'] = list(retlist)
                #build line data base for the subsystem.
                LinkData = []
                srchKeys = ['Name','SrcBlock', 'SrcPort', 'DstBlock', 'DstPort']
                LinkData  = self._getSrchDataFromSubBlck_RCAPI(retlist, 'Line', srchKeys)
                subSystemDetail['LinkData'] = list(LinkData)
                #Get the name of the subsystem and store in the subsystem dictionary.
                GetStats, PropDict, rSubLst = self._getGenericBlckPrpty(retlist, ['Name'])
                if 'Name' in PropDict:
                    subSystemDetail['Name'] = PropDict['Name']
                else:
                    subSystemDetail['Name'] = '<Unknown>'
                self.SubSysData.append(subSystemDetail)
        self.noOfSubsystems = len(self.SubSysData)

    #-------------------------------------------------------------------------------------------

    def _getSrchDataFromBlck_RCAPI(self, inplist, blockName, srchKeys):
        GetStats = []
        PropDict = []
        rSubLst = []
        rCompltLst = []
        # Find the position of the dicitionary main keys in the main list.
        settingPositionlist = list(self._getItemPosition(inplist, blockName))
        #If the position is found then process for the property values.
        if (len(settingPositionlist)) > 0:
            # Loop through each key position
            for settingPosIndex in settingPositionlist:
                # Get the complete block for the key postion.
                srchBlck = self._getCmpleteBlck(inplist, settingPosIndex)
                if (len(srchBlck) > 1):
                    rCompltLst.append(copy.copy(srchBlck))
                    # Provide the search list to the extracted block.
                    tGetStats, tPropDict, trSubLst = self._getGenericBlckPrpty(srchBlck, srchKeys)
                    GetStats.append(tGetStats)
                    PropDict.append(tPropDict)
                    rSubLst.append(trSubLst)
        else:
            GetStats.append(-1)
        return GetStats, PropDict, rSubLst, rCompltLst

    #-------------------------------------------------------------------------------------------

    def _getBlockInfo(self, PropDict):
        '''
        From the input dictionary, check for block type and block key if available and return the
        corresponding value.
        '''
        blockName = '<unknown>'
        blockType = '<unknown>'
        if 'BlockType' in PropDict:
            blockType = PropDict['BlockType']
        if 'Name' in PropDict:
            blockName = PropDict['Name']
        elif 'name' in PropDict:
            blockName = PropDict['name']
        return blockType, blockName

    #-------------------------------------------------------------------------------------------

    def _getSrchDataFromSubBlck_RCAPI(self, inplist, blockName, srchKeys):
        '''
        Search the main list for the requested block. If the requested block is found, Check for the
        requested items in it. If found, append the items and the value to the return dictionary.
        If the block search for main list returns subList entry, then search in the sublist for the
        requested items. if the requested items are found, append/add the items and the value to the
        return dictionary.
        '''
        GetStats = []
        PropDict = []
        rSubLst = []
        InnerDictList = []
        GetStats, PropDict, rSubLst, CompltLst = self._getSrchDataFromBlck_RCAPI(inplist, blockName, srchKeys)
        for searchItem in range(0,len(GetStats)):
            InnerDict = {}
            if GetStats[searchItem] == 1:
                for srchKeyItem in srchKeys:
                    if srchKeyItem in PropDict[searchItem].keys():
                        if srchKeyItem not in InnerDict.keys():
                            InnerDict[srchKeyItem] = []
                            InnerDict[srchKeyItem].append(PropDict[searchItem][srchKeyItem])
                        else:
                            InnerDict[srchKeyItem].append(PropDict[searchItem][srchKeyItem])
                    for SubLstItem in rSubLst[searchItem]:
                        GetSubStats, SubPropDict, rSubSubLst, SubCompltLst = self._getSrchDataFromBlck_RCAPI(CompltLst[searchItem], SubLstItem, srchKeys)
                        for SubsearchItem in range(0,len(GetSubStats)):
                            if GetSubStats[SubsearchItem] == 1:
                                if srchKeyItem in SubPropDict[SubsearchItem].keys():
                                    if srchKeyItem not in InnerDict.keys():
                                        InnerDict[srchKeyItem] = []
                                        InnerDict[srchKeyItem].append(SubPropDict[SubsearchItem][srchKeyItem])
                                    else:
                                        InnerDict[srchKeyItem].append(SubPropDict[SubsearchItem][srchKeyItem])
            InnerDictList.append(InnerDict)
        return InnerDictList


    #-------------------------------------------------------------------------------------------
    # Decide the rule ID based on the configuration setting key type.
    def _getCCSettingRuleID(self, configSetting):
        Rule_ID = ''
        if configSetting == 'Simulink.SolverCC':
            Rule_ID = 'MISRA AC SLSF 003'
        elif configSetting == 'Simulink.DebuggingCC':
            Rule_ID = 'MISRA AC SLSF 004'
        else :
            Rule_ID = 'Configuration Settings Check'
        return Rule_ID

    #-------------------------------------------------------------------------------------------
    # Decide the rule ID based on the configuration setting key type.
    def _compareCCSettingKeys(self, CCSetting, configLst):
        # Decide the rule ID based on the dictionary key type.
        Rule_ID = self._getCCSettingRuleID(CCSetting)
        # From the data dictionary, identify the items to search
        srchKeys = DataDictionary.CCSettingsList[CCSetting].keys()
        for srchKeyItem in srchKeys:
            # Check if the search key found in config list.
            if srchKeyItem in configLst.keys():
                if srchKeyItem == 'BooleanDataType':
                    self.BoolPrtyData['BooleanDataType'] = configLst[srchKeyItem]

                # Compare the parsed dict element with the Data dictionary element.
                self.dataLoggerObj.logCompResult(DataDictionary.CCSettingsList[CCSetting][srchKeyItem],
                    configLst[srchKeyItem], " :: ", 'POSTIVE', self.ModuleName, Rule_ID, 'Configuration Settings ', CCSetting, srchKeyItem,
                        'Failure : Property value does not comply with the standards')
            # if not, raise a warning stating that the proerty is not found.
            else:
                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName, Rule_ID,'Configuration Settings ',
                    ' Error: Property \"'+CCSetting +'\" \"'+ srchKeyItem +'\" is not found in the hierarchy')

    #-------------------------------------------------------------------------------------------

    def _getDefaultProperty(self, InputDict, SrcInput):
        #1) Get the block type of the input dictionary.
        if 'BlockType' in InputDict.keys():
            BlockType = InputDict['BlockType']
            SrchList = ['BlockType']
            #2) Make a list of search keys that are not found in the input dictionary and are to be
            #   searhed in default parameter block
            for ScrInputKeys in SrcInput.keys():
                if ScrInputKeys not in InputDict.keys():
                    SrchList.append(ScrInputKeys)
            #3) In the default parameter block, search for the block type identified in step 1.
            if len(SrchList) > 1:
                GetStats, PropDict, rSubLst, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__DefaultBlkParm, 'Block', SrchList)
                #4) In the searched block, get the values for the parameter list that listed in step 2.
                for searchItem in range(0,len(GetStats)):
                    if GetStats[searchItem] == 1:
                        if 'BlockType' in PropDict[searchItem].keys():
                            if PropDict[searchItem]['BlockType'] == InputDict['BlockType']:
                                SrchList.remove('BlockType')
                                #5) The InputDict reference should be updated with the additional data.
                                for searchAddItem in SrchList:
                                    if searchAddItem in PropDict[searchItem].keys():
                                        InputDict[searchAddItem] = PropDict[searchItem][searchAddItem]
    #-------------------------------------------------------------------------------------------
    def GetActivatedConfigID(self,Poslist,MDLList):
        '''
            This function gives the Activated config ID
        '''
        ConfigID=0	
        # Loop through each key position
        for settingPosIndex in Poslist:
            # Get the complete block for the key postion.
            srchBlck = self._getCmpleteBlck(MDLList, settingPosIndex)
            if (len(srchBlck) > 1):
                # Provide the search list to the extracted block.
                    tGetStats, tPropDict, trSubLst = self._getGenericBlckPrpty(srchBlck, ['$PropName','$ObjectID'])
                    if '$PropName' in tPropDict.keys() and '$ObjectID' in tPropDict.keys():
                        if tPropDict['$PropName'] in ['ActiveConfigurationSet']:
                            ConfigID =  tPropDict['$ObjectID']
                            break
        return ConfigID					
    
    #-------------------------------------------------------------------------------------------

    def checkCCSettings_RCAPI(self):
    #check the CC settings stored in the data dicitionary with the parsed data from the
    #MDL file.
        returnCode = 0
        ActivatedConfigSetObjID = 0

        refCCLst = list(self.__MDLlist)
        # Get the position of the Simulink.ConfigSetRef
        poslist = list(self._getItemPosition(refCCLst, 'Simulink.ConfigSetRef'))
        # Make a copy of the input list.
        refCCLstCopy = list(refCCLst)
        if len(poslist) > 0 :
 
            #check for Activated Config set
            if len(poslist) >= 3:
                ActivatedConfigSetObjID = self.GetActivatedConfigID(poslist,refCCLstCopy)		

            #When .mdl file have only one Config file
            if ActivatedConfigSetObjID == 0:
                 # Loop through each key position
                for settingPosIndex in poslist:
                    # Get the complete block for the key postion.
                    srchBlck = self._getCmpleteBlck(refCCLstCopy, settingPosIndex)
                    if len(srchBlck) > 1:
                        break
                if (len(srchBlck) > 1):
                    # Provide the search list to the extracted block.
                    tGetStats, tPropDict, trSubLst = self._getGenericBlckPrpty(srchBlck, ['WSVarName'])
                    if (tGetStats > 0):
                        filename = 'Unknown'
                        Rule_ID = 'Configuration Settings Check'
                        if tPropDict['WSVarName'] in DataDictionary.configReferenceFiles.keys():
                            filename = DataDictionary.configReferenceFiles[tPropDict['WSVarName']]
                            Mdata = readM(filename)
                            configLst = ParseMfile(Mdata)

                            if (len(configLst) > 0):
                                # Loop through all the dictionary main keys
                                for headDictValue in DataDictionary.CCSettingsList.keys():
                                    self._compareCCSettingKeys(headDictValue, configLst)
                        else:
                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", " :: ", self.ModuleName, Rule_ID,
                                'Configuration Settings  is not found in this module')
            else:#when .mdl file have multiple Config files
                ObjectIDRecived = False
                print 'I reached2'
                 # Loop through each key position
                for settingPosIndex in poslist:
                    # Get the complete block for the key postion.
                    srchBlck = self._getCmpleteBlck(refCCLstCopy, settingPosIndex)
                    if len(srchBlck) >= 2:
                        # Provide the search list to the extracted block.
                        tGetStats, tPropDict, trSubLst = self._getGenericBlckPrpty(srchBlck, ['WSVarName','$ObjectID'])
                        if '$ObjectID' in tPropDict.keys():
                            if tPropDict['$ObjectID'] == ActivatedConfigSetObjID:
                                ObjectIDRecived = True
                                break 
                if ObjectIDRecived == True:
                    print 'I reached1'
                    if (tGetStats > 0):
                        filename = 'Unknown'
                        Rule_ID = 'Configuration Settings Check'
                        if tPropDict['WSVarName'] in DataDictionary.configReferenceFiles.keys():
                            filename = DataDictionary.configReferenceFiles[tPropDict['WSVarName']]
                            Mdata = readM(filename)
                            configLst = ParseMfile(Mdata)

                            if (len(configLst) > 0):
                                # Loop through all the dictionary main keys
                                for headDictValue in DataDictionary.CCSettingsList.keys():
                                    self._compareCCSettingKeys(headDictValue, configLst)
                        else:
                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", " :: ", self.ModuleName, Rule_ID,
                                'Configuration Settings  is not found in this module')
        else :
            # Loop through all the dictionary main keys
            for headDictValue in DataDictionary.CCSettingsList.keys():
                # Decide the rule ID based on the dictionary key type.
                Rule_ID = self._getCCSettingRuleID(headDictValue)

                # From the data dictionary, identify the items to search
                srchKeys = DataDictionary.CCSettingsList[headDictValue].keys()

                # Get search Data
                GetStats, PropDict, rSubLst, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__MDLlist, headDictValue, srchKeys)
                #process only if something is found in the list.
                for searchItem in range(0,len(GetStats)):
                    if GetStats[searchItem] == 1:
                        # For each key in dictionary, check the corresponding property value
                        self._compareCCSettingKeys(headDictValue, PropDict[searchItem])
                    # if the block is not found, state a remark.
                    elif GetStats[searchItem] == -1:
                        self.dataLoggerObj.logCondResult("-", "-", "PASS", " :: ", self.ModuleName, Rule_ID, 'Configuration Settings ',
                                               'Information: Property \"' + headDictValue + '\" is not found in this module')

    #-------------------------------------------------------------------------------------------

    def checkdebuggCC_RCAPI(self, Rule_ID):
    #check the CC settings stored in the data dicitionary with the parsed data from the
    #MDL file.
        returnCode = 0
        #Rule_ID = 'HISL_0013 A'
        srchKeys = []
        srchKeys = DataDictionary.DataStoreCC[Rule_ID]
        GetStats, PropDict, rSubLst, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__MDLlist, 'Simulink.DebuggingCC', srchKeys)
        if len(PropDict) > 0:
            for searchItem in range(0,len(srchKeys)):
                    for srchKeysPos in range(0,len(PropDict[0])):
                        if srchKeys.keys()[searchItem] == PropDict[0].keys()[srchKeysPos]:
                            if srchKeys.values()[searchItem] == PropDict[0].values()[srchKeysPos]:
                                self.dataLoggerObj.logCondResult("-", "-", "PASS", " :: ", self.ModuleName, Rule_ID, 'Configuration Settings ',
                                       'Information: Property \"'  '\" is not found in this module')
                            else:
                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", " :: ", self.ModuleName, Rule_ID, 'Configuration Settings ',
                                       'Failure : Property value of \"'+PropDict[0].keys()[srchKeysPos]+'" does not comply with the standards value')
        elif GetStats[0] == -1:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", " :: ", self.ModuleName, Rule_ID, 'Configuration Settings ',
                                  'Information: Property \"'  '\" is not found in this module')

    #-------------------------------------------------------------------------------------------

    def checkAllowedBlocks_RCAPI(self):
    #check the Allowed Block list stored in the data dicitionary with the parsed data from the
    #MDL file.

        Rule_ID = 'RP_0054'

        GetStats, PropDict, rSubLst, CompltLst =\
            self._getSrchDataFromBlck_RCAPI(self.__DefaultBlkParm, 'Block', ['BlockType'])

        if GetStats > 0:
            #Check if the block is an allowed block
            for searchItem in range(0,len(GetStats)):
                blockTypeAllowed = False
                blocktype = str(PropDict[searchItem]['BlockType'])
                for headDictValue in DataDictionary.AllowedOtherBlocks:
                    #From the data dictionary, identify the items to search
                    if headDictValue == PropDict[searchItem]['BlockType']:
                        blockTypeAllowed = True
                        break
                #Check if the block is an allowed Subsystem Block
                if blockTypeAllowed == False:
                    if PropDict[searchItem]['BlockType'] == 'SubSystem' :
                        inpLst, foundLst, Name = self._getNextList()
                        while (foundLst == True):
                            if Name != self.ModuleName:
                                subsystemTypeAllowed = True
                                propItemChecked = 0
                                for headDictValue in DataDictionary.AllowedSubsystemBlocks.keys():
                                    srchKeys = []
                                    srchKeys.append('BlockType')
                                    srchKeys.append('Name')
                                    srchKeys.append(headDictValue)
                                    LinkData = self._getSrchDataFromSubBlck_RCAPI(inpLst['List'], 'Block', srchKeys)
                                    if len(LinkData) > 0:
                                        for index in range(0,len(LinkData)):
                                            if headDictValue in LinkData[index]:
                                                propItemChecked = propItemChecked + 1
                                                if LinkData[index][headDictValue][0] not in\
                                                    DataDictionary.AllowedSubsystemBlocks[headDictValue]:
                                                    subsystemTypeAllowed = False

                                if (subsystemTypeAllowed == False) or (propItemChecked == 0):
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName, Rule_ID,'Block ',
                                        'Error: Block  \"'+Name +'\" is not found in the List')
                                else:
                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", " :: ", self.ModuleName, Rule_ID,'Block ',
                                        'Block \"'+Name +'\" is allowed')

                            inpLst, foundLst, Name = self._getNextList()
                        blockTypeAllowed = True

                #Check if the block is an allowed ModelReference Block
                if blockTypeAllowed == False:
                    if PropDict[searchItem]['BlockType'] == 'ModelReference' :
                        inpLst, foundLst, Name = self._getNextList()
                        while (foundLst == True):
                            for headDictValue in DataDictionary.AllowedModelReferenceBlocks.keys():
                                srchKeys = []
                                srchKeys.append('BlockType')
                                srchKeys.append('Name')
                                srchKeys.append(headDictValue)
                                propItemChecked = 0
                                LinkData = self._getSrchDataFromSubBlck_RCAPI(inpLst['List'], 'Block', srchKeys)
                                if len(LinkData) > 0:
                                    for index in range(0,len(LinkData)):
                                        if headDictValue in LinkData[index]:
                                            if LinkData[index]['BlockType'][0] == 'ModelReference':
                                                modelRefTypeAllowed = True
                                                if LinkData[index][headDictValue][0] not in\
                                                    DataDictionary.AllowedModelReferenceBlocks[headDictValue]:
                                                    modelRefTypeAllowed = False

                                                if modelRefTypeAllowed == False:
                                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName, Rule_ID,'Block ',
                                                        ' Error: Block  \"'+Name +'\" is not found in the List')
                                                else:
                                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", " :: ", self.ModuleName, Rule_ID,'Block ',
                                                        'Block \"'+Name +'\" is allowed')

                            inpLst, foundLst, Name = self._getNextList()
                        blockTypeAllowed = True

                if blockTypeAllowed == False:
                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName, Rule_ID,'Block ',
                        ' Error: Block Type \"'+blocktype +'\" is not found in the List')
                else:
                    self.dataLoggerObj.logCondResult("-", "-", "PASS", " :: ", self.ModuleName, Rule_ID,'Block ',
                        'Block Type \"'+blocktype +'\" is allowed')

        #Check if the block is an allowed Reference Block
        inpLst, foundLst, Name = self._getNextList()
        while (foundLst == True):
            for headDictValue in DataDictionary.AllowedReferenceBlocks.keys():
                srchKeys = []
                srchKeys.append('BlockType')
                srchKeys.append('Name')
                srchKeys.append(headDictValue)
                LinkData = self._getSrchDataFromSubBlck_RCAPI(inpLst['List'], 'Block', srchKeys)
                if len(LinkData) > 0:
                    for index in range(0,len(LinkData)):
                        refTypeAllowed = True
                        if 'BlockType' in LinkData[index].keys():
                            if LinkData[index]['BlockType'][0] == 'Reference':
                                if headDictValue in LinkData[index]:
                                    if LinkData[index][headDictValue][0] not in\
                                        DataDictionary.AllowedReferenceBlocks[headDictValue]:
                                        refTypeAllowed = False

                                refName = str(LinkData[index]['Name'][0])
                                if refTypeAllowed == False:
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName, Rule_ID,'Block ',
                                        ' Error: Block  \"'+refName +'\" is not found in the List')
                                else:
                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", " :: ", self.ModuleName, Rule_ID,'Block ',
                                        'Block \"'+refName +'\" is allowed')
            inpLst, foundLst, Name = self._getNextList()

    #-------------------------------------------------------------------------------------------

    def checkAttributesFormatString_RCAPI(self):
    #check the Allowed Attributes Format String stored in the data dicitionary with the parsed data from the
    #MDL file.

        Rule_ID = 'RP_0008'

        srchKeys = []
        srchKeys.append('AttributesFormatString')
        srchKeys.append('BlockType')

        inpLst, foundLst, Name = self._getNextList()
        while (foundLst == True):
            GetStats, PropDict, rSubLst, CompltLst =\
                self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Block', srchKeys)
            if len(GetStats) > 0:
                #Check if the Blocks defined in Sheet AttritubeFormatStrings and their value match
                for searchItem in range(0,len(GetStats)):
                    blockTypeFound = False
                    try:
                        for headDictValue in DataDictionary.AttributesFormatString.keys():
                            #From the data dictionary, identify the items to search
                            if headDictValue == PropDict[searchItem]['BlockType']:
                                blockTypeFound = True
                                break
                    except:
                        pass

                    if blockTypeFound == True:
                        if 'AttributesFormatString' in PropDict[searchItem].keys():
                            self.dataLoggerObj.logCompResult(DataDictionary.AttributesFormatString[headDictValue], PropDict[searchItem]['AttributesFormatString'], " :: ", 'POSTIVE', self.ModuleName,
                                 Rule_ID, 'Failure - The value of Attrubute format string in block"'+headDictValue+'\" does not comply')
            inpLst, foundLst, Name = self._getNextList()

    #-------------------------------------------------------------------------------------------

    def checkReusableLib_RCAPI(self, Rule_ID, InpList, UniqueKey, PropChkData, ExceptionModule = []):
    # check if the signals originating for reusable blocks aer not labelled
        inpLst = list(InpList)
        srchKey  = UniqueKey[0]
        if self.ModuleName not in ExceptionModule:
            # Get list positions of the reuseable blocks
            posList = list(self._getItemPosition(self.__MDLlist, srchKey))
            for settingPosIndex in posList:
                # Get complete block data for reuseable blocks
                MaskTypeFound = False
                srchUnkeyBlck = self._getCmpleteBlck(inpLst, settingPosIndex[:-1])
                for srchUnkeyBlckItem in srchUnkeyBlck:
                    # For each reusable blocks in reusable blocklist
                    if (srchUnkeyBlckItem[0] == srchKey and (srchUnkeyBlckItem[1] in DataDictionary.ReusableLibList)):
                        posListType = list(self._getItemPosition(srchUnkeyBlck, UniqueKey[1]))
                        # To find signals originating for reusable blocks
                        for settingPosIndex in posListType:
                            srchListTypeBlck = self._getCmpleteBlck(srchUnkeyBlck, settingPosIndex[:-1])
                            srchListTypeBlckDict = dict(srchListTypeBlck)
                            keyList=list(srchListTypeBlckDict)
                            if srchListTypeBlckDict[keyList[0]] == PropChkData:
                                for item in keyList[1:]:
                                    # If signals originating for reusable blocks aer not labelled
                                    if srchListTypeBlckDict[item] == '':
                                        self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                     Rule_ID, 'Signal originating from reusable block '+srchUnkeyBlckItem[1]+' is not labelled inside the subsytem.')
                                    # else
                                    else:
                                        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                     Rule_ID, 'Signal item \"'+item+'\" originating from reusable block \"'+srchUnkeyBlckItem[1]+'\" is labelled as \"'+srchListTypeBlckDict[item]+'\" inside the subsytem.')
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                Rule_ID, 'Check for reusable block property is excluded in this Module')

	#-------------------------------------------------------------------------------------------

    def checkReusableLib_RCAPI(self, Rule_ID, srchKeys, PropChkData, ExceptionModule = []):
    # check if the signals originating for reusable blocks aer not labelled

        if self.ModuleName not in ExceptionModule:
            # Get the reuseable blocks used in the model under check
            refNameList = []
            inpLst1, foundLst1, Name1= self._getNextList()
            while (foundLst1 == True):
                GetStats, PropDict, rSubLst, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst1['List'], 'Block', srchKeys)
                for blockItem in PropDict:
                    try:
                        if (blockItem[srchKeys[0]] == 'Reference') and (blockItem[srchKeys[1]] in DataDictionary.ReusableLibList):
                                refNameList.append(blockItem[srchKeys[2]])
                        elif (blockItem[srchKeys[0]] == 'ModelReference') and (blockItem[srchKeys[3]] in DataDictionary.ReusableLibList):
                                refNameList.append(blockItem[srchKeys[2]])
                    except:
                        pass
                inpLst1, foundLst1, Name1 = self._getNextList()

            # check if the signal originating from reusable block is labelled
            inpLst, foundLst, Name = self._getNextList()
            while (foundLst == True):
                if 'Name' in inpLst.keys():
                    system_Tag = 'Subsystem'
                else:
                    system_Tag = 'System'

                # for each link data item
                for LinkItem in inpLst['LinkData']:
                    # if any of the reusable block is the source of the signal
                    if PropChkData[0] in LinkItem.keys():
                        if LinkItem[PropChkData[0]][0] in refNameList:
                            try:
                                # checl signal is not labelled
                                if LinkItem[PropChkData[1]][0] == '':
                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                        Rule_ID, 'In model \"'+self.ModuleName+'\", '+system_Tag+' \"'+Name+'\" the ouput signal originating from \"'+LinkItem[PropChkData[0]][0]+'\" is not labelled.')
                                else:
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                        Rule_ID, 'In model \"'+self.ModuleName+'\", '+system_Tag+' \"'+Name+'\" the ouput signal originating from \"'+LinkItem[PropChkData[0]][0]+'\" is labelled.')
                            except:
                                    # if there is no name attribute with the signal, then pass
                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                        Rule_ID, 'In model \"'+self.ModuleName+'\", '+system_Tag+' \"'+Name+'\" the ouput signal originating from \"'+LinkItem[PropChkData[0]][0]+'\" is not labelled.')
                inpLst, foundLst, Name = self._getNextList()

        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                Rule_ID, 'Check for reusable block property is excluded in this Module')

	#-------------------------------------------------------------------------------------------

    def checkPropDoNotExists_RCAPI(self, Rule_ID, model, propname, ExceptionModule = []):
        # Find the prperty name in the parsed data, if not the list will be empty
        expres = propname + ' should not exist'
        passactres = propname + ' does not exist'
        failactres = propname + ' exists'
        if self.ModuleName not in ExceptionModule:
            if model == 'SIMULINK_MODEL':
                no_of_occ = len(list(self._getItemPosition(self.__MDLlist, propname)))
                if (no_of_occ == 0):
                    self.dataLoggerObj.logCondResult(expres, passactres, 'PASS', " :: ",
                        self.ModuleName, Rule_ID, passactres + ' in this module')
                else:
                    self.dataLoggerObj.logCondResult(expres, failactres, 'FAIL', " :: ",
                        self.ModuleName, Rule_ID, 'The use of property \"'+propname + '\" is not allowed in this module')

            elif model == 'SIMULINK_BLOCK':
                inpLst, foundLst, Name = self._getNextList()
                while (foundLst == True):
                    no_of_occ = len(list(self._getItemPosition(inpLst['List'], propname)))
                    if (no_of_occ == 0):
                        self.dataLoggerObj.logCondResult(expres, passactres, 'PASS', " :: ",
                            self.ModuleName, Rule_ID, passactres + ' in this module')
                    else:
                        self.dataLoggerObj.logCondResult(expres, failactres, 'FAIL', " :: ",
                            self.ModuleName, Rule_ID, 'The use of property \"'+propname + '\" is not allowed in this module')
                    inpLst, foundLst, Name = self._getNextList()

            else:
                no_of_occ = len(list(self._getItemPosition(self.__SFlist, propname)))
                if (no_of_occ == 0):
                    self.dataLoggerObj.logCondResult(expres, passactres, 'PASS', " :: ",
                        self.ModuleName, Rule_ID, passactres + ' in this module')
                else:
                    self.dataLoggerObj.logCondResult(expres, failactres, 'FAIL', " :: ",
                        self.ModuleName, Rule_ID, 'The use of property \"'+propname + '\" is not allowed in this module')
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                Rule_ID, 'Check for \"'+ propname +'\" property is excluded in this Module')


    #-------------------------------------------------------------------------------------------
    def checkPrtyShouldExist_RCAPI(self,Rule_ID,PropName,SrchKeys):
        '''
            DocBlock should exist in every model file at root level
        '''
        SubSystmNames,SubSystemPrptyInfo1D,SubSystmPrptyInfo2D,LineInfoOfMdl,SubSystmPrptyInfo4D,SubSystmPrptyInfo8D,RootLevelSystemInfo=self.SubSystemNamesUtil()
        inpLst = RootLevelSystemInfo['List']
        GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst, 'Block', SrchKeys)
        ResultCount=0
        for BlockIndex in range(0,len(PropDictS1)):
            if 'BlockType' in PropDictS1[BlockIndex].keys():
                if 'SourceType' in PropDictS1[BlockIndex].keys():
                    if PropDictS1[BlockIndex]['SourceType'] == 'DocBlock':
                        if 'ECoderFlag' in PropDictS1[BlockIndex].keys():
                            if PropDictS1[BlockIndex]['ECoderFlag'] == PropName:
                                ResultCount = ResultCount+1
        if ResultCount >0:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                Rule_ID, 'DocBlock of Type /"'+PropName+'" exist at root Level')
        else:
            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                Rule_ID, 'DocBlock \"'+PropName+'" do not exist at root Level with name of \"'+PropName+'"')
    #------------------------------------------------------------------------------------------

    def checkGenericPropValueInList_RCAPI(self, Rule_ID, PropChkData, UniqueKey, inplist, ExceptionModule = []):
        # Find the prperty name in the parsed data, if not the list will be empty
        ruleApplicability = 0
        blockinfo = ''
        if self.ModuleName not in ExceptionModule:
            for propItem in PropChkData.keys():
                settingPositionlist = list(self._getItemPosition(inplist, propItem))
                #If the position is found then process for the property values.
                if (len(settingPositionlist)) > 0:
                    # Loop through each key position
                    for settingPosIndex in settingPositionlist:
                        # Get search Data
                        srchUnkeyBlck = self._getCmpleteBlck(inplist, settingPosIndex[:-1])
                        # Provide the search list to the extracted block.
                        GetStats, PropDict, rSubLst = self._getGenericBlckPrpty(srchUnkeyBlck, UniqueKey)
                        if GetStats == 1:
                            for uqitem in UniqueKey:
                                if uqitem in PropDict.keys():
                                    blockinfo = PropDict[uqitem]
                                    break
                        # Get the complete block for the key postion.
                        srchBlck = self._getCmpleteBlck(inplist, settingPosIndex)
                        # Check if the property has only on value
                        if (len(srchBlck) == 1):
                            try:
                               # Compare the parsed parsed property value with the supplied value.
                                self.dataLoggerObj.logCompResult(PropChkData[propItem], srchBlck[0], " :: ", 'POSTIVE', self.ModuleName,
                                      Rule_ID, 'Failure - The value of property \"'+propItem+'\" in block '+uqitem+' \"'+blockinfo+ '\" does not comply')
                            except:
                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                    Rule_ID, ' Error - Property \"'+propItem+'\" value is not found or has multiple values')
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

    #-------------------------------------------------------------------------------------------

    def checkSystemPropValueInBlock_RCAPI(self, Rule_ID, PropChkData, UniqueKey, ExcludeBlock = [], ExceptionModule = [], checkType = 'POSTIVE'):
        '''
        Search the default block parameter blocks for the requested property.
        If property exists, note down the property value and the block type.
        In each block of block type found from default parameter, search the property.
        If property exists, check the value with the expected prop value. Otherwise,
        Check the expected property against the noted property.
        '''
        if self.ModuleName not in ExceptionModule:
            for propItem in PropChkData.keys():
                srchKeys = []
                DefaultBlkData = {}
                blockinfo = []
                settingPositionlist = list(self._getItemPosition(self.__DefaultBlkParm, propItem))
                #If the position is found then process for the property values.
                if (len(settingPositionlist)) > 0:
                    # Loop through each key position
                    for settingPosIndex in settingPositionlist:
                        # Get search Data
                        srchUnkeyBlck = self._getCmpleteBlck(self.__DefaultBlkParm, settingPosIndex[:-1])
                        # Provide the search list to the extracted block.
                        blockinfo.append(UniqueKey[0])
                        GetStats, PropDict, rSubLst = self._getGenericBlckPrpty(srchUnkeyBlck, blockinfo)
                        blockType = PropDict[UniqueKey[0]]
                        # Get the complete block for the key postion.
                        srchBlck = self._getCmpleteBlck(self.__DefaultBlkParm, settingPosIndex)
                        # Check if the property has only on value
                        if (len(srchBlck) == 1) and (blockType not in ExcludeBlock):
                            DefaultBlkData[blockType] = srchBlck[0]

                for DefaultBlckItem in DefaultBlkData.keys():
                    srchKeys.append(propItem)
                    srchKeys+=UniqueKey
                    inpLst, foundLst, Name = self._getNextList()
                    while (foundLst == True):
                        GetStats, PropDict, rSubLst, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Block', srchKeys)
                        #process only if something is found in the list.
                        for searchItem in range(0,len(GetStats)):
                            if GetStats[searchItem] == 1:
                                if UniqueKey[0] in PropDict[searchItem].keys():
                                    if PropDict[searchItem][UniqueKey[0]] == DefaultBlckItem:
                                        if UniqueKey[1] in PropDict[searchItem].keys():
                                            BlockName = PropDict[searchItem][UniqueKey[1]]
                                        else:
                                            BlockName = ''
                                        if propItem in PropDict[searchItem].keys():
                                           # Compare the parsed parsed property value with the supplied value.
                                            self.dataLoggerObj.logCompResult(PropChkData[propItem], PropDict[searchItem][propItem], " :: ", checkType, self.ModuleName,
                                                  Rule_ID, 'Failure - The value of property \"'+propItem+'\" in block \"'+BlockName+'\" of type \"'+DefaultBlckItem+'\" does not comply')
                                        else:
                                           # Compare the parsed parsed property value with the supplied value.
                                            self.dataLoggerObj.logCompResult(PropChkData[propItem], DefaultBlkData[DefaultBlckItem], " :: ", checkType, self.ModuleName,
                                                  Rule_ID, 'Failure - The value of property \"'+propItem+'\" in block \"'+BlockName+'\" of type \"'+DefaultBlckItem+'\" does not comply')
                        inpLst, foundLst, Name = self._getNextList()

        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

    #-------------------------------------------------------------------------------------------

    def _compareBlockProp(self, Rule_ID, PropChkData, PropDict, propItem, BlockType, BlockName, CheckType):
        if CheckType == 'Exact':
            self.dataLoggerObj.logCompResult(PropChkData[propItem], PropDict[propItem], " :: ", 'POSTIVE', self.ModuleName,
                  Rule_ID, 'Failure - The value of property \"'+propItem+'\" in block \"'+BlockName+'\" of type \"'+BlockType+'\" does not comply')
        elif CheckType == 'EndsWith':
                if PropDict[propItem].endswith(PropChkData[propItem]) == True:
                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                         Rule_ID, 'The value of property \"'+propItem+'\" in State ID \"'+BlockName+'\" ends with \"'+PropChkData[propItem]+'\"')
                else:
                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                         Rule_ID, 'The value of property \"'+propItem+'\" in State ID \"'+BlockName+'\" does not ends with \"'+PropChkData[propItem]+'\"')
        elif CheckType == 'Any':
            if PropDict[propItem] != '':
                self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                     Rule_ID, 'The value of property \"'+propItem+'\" in block \"'+BlockName+'\" of type \"'+BlockType+'\" is not empty string')
            else:
                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                     Rule_ID, 'The value of property \"'+propItem+'\" in block \"'+BlockName+'\" of type \"'+BlockType+'\" is empty string')
        elif CheckType == 'Greater':
            # Convert the PropValue into integer
            if int(PropDict[propItem]) > PropChkData[propItem]:
                self.dataLoggerObj.logCondResult(PropChkData[propItem], int(PropDict[propItem]), "PASS", "::", self.ModuleName,
                     Rule_ID, 'The value of property \"'+propItem+'\" in block \"'+BlockName+'\" of type \"'+BlockType+'\" is greater')
            else:
                self.dataLoggerObj.logCondResult(PropChkData[propItem], int(PropDict[propItem]), "FAIL", "::", self.ModuleName,
                     Rule_ID, 'The value of property \"'+propItem+'\" in block \"'+BlockName+'\" of type \"'+BlockType+'\" is not greater')

    #-------------------------------------------------------------------------------------------

    def checkPropValueByBlockType_RCAPI(self, Rule_ID, ListType, PropChkData, BlockType, UniqueKey, CheckType = 'Exact', ExcludeBlock = [], ExceptionModule = []):
        '''
        In each block of the requested block type, search the property.
        If property exists, check the value with the expected prop value. Otherwise,
        Check the expected property against the noted property.
        '''
        if self.ModuleName not in ExceptionModule:
            for propItem in PropChkData.keys():
                srchKeys = []
                DefaultBlkData = {}
                blockinfo = []
                srchKeys.append(propItem)
                srchKeys+=UniqueKey
                inpLst, foundLst, Name = self._getNextList()
                while (foundLst == True):
                    GetStats, PropDict, rSubLst, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], ListType, srchKeys)
                    #process only if something is found in the list.
                    for searchItem in range(0,len(GetStats)):
                        if GetStats[searchItem] == 1:
                            if UniqueKey[0] in PropDict[searchItem].keys():
                                if PropDict[searchItem][UniqueKey[0]] == BlockType:
                                    if UniqueKey[1] in PropDict[searchItem].keys():
                                        BlockName = PropDict[searchItem][UniqueKey[1]]
                                    else:
                                        BlockName = ''
                                    if propItem in PropDict[searchItem].keys():
                                        self._compareBlockProp(Rule_ID, PropChkData, PropDict[searchItem], propItem, BlockType, BlockName, CheckType)
                                    else:
                                        self._getDefaultProperty(PropDict[searchItem], PropChkData)
                                        if propItem in PropDict[searchItem].keys():
                                            self._compareBlockProp(Rule_ID, PropChkData, PropDict[searchItem], propItem, BlockType, BlockName, CheckType)
                    inpLst, foundLst, Name = self._getNextList()
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')
    #-------------------------------------------------------------------------------------------
    def checkOutputshouldConnectActionPort_RCAPI(self,Rule_ID,blckType,DstPort,srchKeys,ExceptionModule = []):
        '''
		10B:Take the block the which have BlockType If and also check "ElseIfExpressions" property
            activated or not ,if activated then check the Line SrcBlock name matches to If block name.
            if both the names are matched then check for DstPort = ifaction property in the same Line
            data.
        11B:take the name of switchcase block and compare with Line data if match the check for
            DstPort = ifaction property.
		'''
        if self.ModuleName not in ExceptionModule:
                inpLst, foundLst, Name = self._getNextList()
                while (foundLst == True):
                    GetStats, PropDict, rSubLst, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Block', srchKeys)
                    GetStats2, PropDict2, rSubLst2, CompltLst2 = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Line', ['SrcBlock','DstPort'])
                    for SrchItem in range(0,len(PropDict)):
                        countItem = 0
                        if blckType == 'IfExist':
                            if PropDict[SrchItem]['BlockType'] == 'If':
                                if 'ElseIfExpressions' in PropDict[SrchItem].keys():
                                    if 'Ports' in PropDict[SrchItem].keys():
                                        noOfOutputPorts = PropDict[SrchItem]['Ports'][1]
                                        for LineIndex in range(0,len(PropDict2)):
                                            if 'SrcBlock' in PropDict2[LineIndex].keys():
                                                if PropDict2[LineIndex]['SrcBlock'] == PropDict[SrchItem]['Name']:
                                                    if 'DstPort' in PropDict2[LineIndex].keys():
                                                        if PropDict2[LineIndex]['DstPort'] == 'ifaction':
                                                            countItem = countItem + 1
                                        if countItem == noOfOutputPorts:
                                            self.dataLoggerObj.logCondResult("-","-","PASS","::",self.ModuleName,Rule_ID,'all outputs of If Block \"'+PropDict[SrchItem]['Name']+'"has connected to IfActionSubSystem in \"'+Name+'"')
                                        else:
                                            self.dataLoggerObj.logCondResult("-","-","FAIL","::",self.ModuleName,Rule_ID,'all outputs of If Block \"'+PropDict[SrchItem]['Name']+'"should be connected to IfActionSubSystem in \"'+Name+'"')
                        else:
                            if blckType == 'SwitchCaseExist':
                                if PropDict[SrchItem]['BlockType'] == 'SwitchCase':
                                    if 'Ports' in PropDict[SrchItem].keys():
                                        noOfOutputPorts = PropDict[SrchItem]['Ports'][1]
                                        for LineIndex in range(0,len(PropDict2)):
                                            if 'SrcBlock' in PropDict2[LineIndex].keys():
                                                if PropDict2[LineIndex]['SrcBlock'] == PropDict[SrchItem]['Name']:
                                                    if 'DstPort' in PropDict2[LineIndex].keys():
                                                        if PropDict2[LineIndex]['DstPort'] == 'ifaction':
                                                            countItem = countItem + 1
                                        if countItem == noOfOutputPorts:
                                            self.dataLoggerObj.logCondResult("-","-","PASS","::",self.ModuleName,Rule_ID,'all outputs of SwitchCase Block \"'+PropDict[SrchItem]['Name']+'"has connected to IfActionSubSystem in \"'+Name+'"')
                                        else:
                                            self.dataLoggerObj.logCondResult("-","-","FAIL","::",self.ModuleName,Rule_ID,'all outputs of SwitchCase Block \"'+PropDict[SrchItem]['Name']+'"should be connected to IfActionSubSystem in \"'+Name+'"')

                    inpLst, foundLst, Name = self._getNextList()

    #-------------------------------------------------------------------------------------------
    # API not used by any rule.
    def checkPropValueByStateFlowType_RCAPI(self, Rule_ID, ListType, PropChkData, UniqueKey, CheckType = 'Exact', ExcludeBlock = [], ExceptionModule = []):
        '''
        In each block of the requested State flow type, search the property.
        If property exists, check the value with the expected prop value. Otherwise,
        Check the expected property against the noted property.
        '''
        if self.ModuleName not in ExceptionModule:
            for propItem in PropChkData.keys():
                srchKeys = []
                DefaultBlkData = {}
                blockinfo = []
                srchKeys.append(propItem)
                srchKeys+=UniqueKey
                GetStats, PropDict, rSubLst, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__SFlist, ListType, srchKeys)
                #process only if something is found in the list.
                for searchItem in range(0,len(GetStats)):
                    if GetStats[searchItem] == 1:
                        if UniqueKey[0] in PropDict[searchItem].keys():
                            StateId = PropDict[searchItem][UniqueKey[0]]
                        else:
                            StateId = ''
                        if propItem in PropDict[searchItem].keys():
                            self._compareBlockProp(Rule_ID, PropChkData, PropDict[searchItem], propItem, [], str(StateId), CheckType)
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')
    #-------------------------------------------------------------------------------------------

    def chkPropValByCond_RCAPI(self, Rule_ID, ListType, PropChkData, CheckListData, ExcludeBlock = [], ExceptionModule = []):
        '''
        In each block of the requested block type, search the property.
        If property exists, check the value with the expected prop value. Otherwise,
        Check the expected property against the noted property.
        '''
        if self.ModuleName not in ExceptionModule:
            tsrchKeys = []
            tsrchKeys+=PropChkData.keys()
            tsrchKeys+=CheckListData.keys()
            tsrchKeys+=['BlockType', 'Name']
            srchKeys = list(set(tsrchKeys))
            inpLst, foundLst, Name = self._getNextList()
            while (foundLst == True):
                GetStats, PropDict, rSubLst, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], ListType, srchKeys)
                for searchItem in range(0,len(GetStats)):
                    if GetStats[searchItem] == 1:
                        blockName = '<unknown>'
                        blockType = '<unknown>'
                        blockType, blockName = self._getBlockInfo(PropDict[searchItem])
                        DataChck = len(PropChkData)
                        for Keyitem in PropChkData:
                            if Keyitem in PropDict[searchItem]:
                                if Keyitem == 'BlockType':
                                    if PropDict[searchItem][Keyitem] in ExcludeBlock:
                                        DataChck +=2 # To exclude from the check.
                                if PropDict[searchItem][Keyitem] == PropChkData[Keyitem]:
                                    DataChck -= 1

                            if DataChck == 0:
                                for checkItem in CheckListData:
                                    if checkItem in PropDict[searchItem]:
                                        # Compare the parsed parsed property value with the supplied value.
                                        self.dataLoggerObj.logCompResult(CheckListData[checkItem], PropDict[searchItem][checkItem], " :: ", 'POSTIVE', self.ModuleName,
                                             Rule_ID, 'Failure - The value of property \"'+checkItem+'\" in block \"'+blockName+' of type \"'+blockType+'\" does not comply with the rule')
                inpLst, foundLst, Name = self._getNextList()
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

   #-------------------------------------------------------------------------------------------
    '''
           Misra 17A
    '''
    def checkNoUnconnectedBlocks_RCAPI(self,Rule_Id,BlockList,AllowedBlockList,ExceptionModule = ['reusable_lib']):

        if self.ModuleName not in ExceptionModule:
            SubSystemNames,SubSystemPrptyInfo1D,SubSystemPrptyInfo2D,LineInfoOfModel,SubSystemPrptyInfo4D,SubSystemPrptyInfo8D,SystmInfo = self.SubSystemNamesUtil()

            inpLst, foundLst, Name = self._getNextList()
            LineDataSrchKeys = ['SrcBlock','DstBlock']
            while (foundLst == True):
                #get the Block and Line data with SearchKeys.
                GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Block', ['BlockType','Name','Ports'])
                GetStatsS2, PropDictS2, rSubLstS2, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Line', LineDataSrchKeys)
                for  BlockIndex in range(0,len(PropDictS1)):

                    #for either ['Inport','From','Ground','Constant'] Blocks
                    if PropDictS1[BlockIndex]['BlockType'] in AllowedBlockList[0]:
                        if 'Name' in PropDictS1[BlockIndex].keys():
                            NameOfBlock = PropDictS1[BlockIndex]['Name']
                            PortName = 'Output'
                            ports = 1   #The blocks which contain only one Outport Data.
                            self.NoUnconnectedBlocksUtil(PropDictS2,NameOfBlock,PortName,ports,PropDictS1[BlockIndex]['BlockType'],self.ModuleName,Rule_Id,Name,'SrcBlock','DstBlock')
                    else:
                        #for either ['Goto','Outport','Terminator'] Blocks
                        if PropDictS1[BlockIndex]['BlockType'] in AllowedBlockList[1]:
                            if 'Name' in PropDictS1[BlockIndex].keys():
                                NameOfBlock = PropDictS1[BlockIndex]['Name']
                                PortName = 'Input'
                                ports = 1 #these three blocks contain only one Input Data.
                                self.NoUnconnectedBlocksUtil(PropDictS2,NameOfBlock,PortName,ports,PropDictS1[BlockIndex]['BlockType'],self.ModuleName,Rule_Id,Name,'DstBlock','SrcBlock')
                        else:
                            #This is for all 2D-vary vector Blocks
                            if  PropDictS1[BlockIndex]['BlockType'] in  AllowedBlockList[2]:
                                if 'Name' in PropDictS1[BlockIndex].keys():
                                    NameOfBlock = PropDictS1[BlockIndex]['Name']
                                if 'Ports' in PropDictS1[BlockIndex].keys():
                                    ports = PropDictS1[BlockIndex]['Ports']
                                    if len(ports) == 2:
                                        #checking for input ports.
                                        PortName = 'Input'
                                        NumberOfInputPorts = ports[0]
                                        self.NoUnconnectedBlocksUtil(PropDictS2,NameOfBlock,PortName,NumberOfInputPorts,PropDictS1[BlockIndex]['BlockType'],self.ModuleName,Rule_Id,Name,'DstBlock','SrcBlock')

                                        #checking for output ports
                                        PortName = 'Output'
                                        NumberOfOutputtPorts = ports[1]
                                        self.NoUnconnectedBlocksUtil(PropDictS2,NameOfBlock,PortName,NumberOfOutputtPorts,PropDictS1[BlockIndex]['BlockType'],self.ModuleName,Rule_Id,Name,'SrcBlock','DstBlock')
                            else:
                                #This is for all 2D-fixed vector Blocks
                                if PropDictS1[BlockIndex]['BlockType'] in  AllowedBlockList[3]:
                                    if 'Name' in PropDictS1[BlockIndex].keys():
                                        NameOfBlock = PropDictS1[BlockIndex]['Name']
                                        #checking for input ports.
                                        PortName = 'Input'
                                        NumberOfInputPorts = 1
                                        self.NoUnconnectedBlocksUtil(PropDictS2,NameOfBlock,PortName,NumberOfInputPorts,PropDictS1[BlockIndex]['BlockType'],self.ModuleName,Rule_Id,Name,'DstBlock','SrcBlock')

                                        #checking for output ports
                                        PortName = 'Output'
                                        NumberOfOutputtPorts = 1
                                        self.NoUnconnectedBlocksUtil(PropDictS2,NameOfBlock,PortName,NumberOfOutputtPorts,PropDictS1[BlockIndex]['BlockType'],self.ModuleName,Rule_Id,Name,'SrcBlock','DstBlock')
                                else:
                                    #This is Only for LookUp2D and Switch block.
                                    if PropDictS1[BlockIndex]['BlockType'] in  AllowedBlockList[4].keys():
                                        if 'Name' in PropDictS1[BlockIndex].keys():
                                            NameOfBlock = PropDictS1[BlockIndex]['Name']
                                            ports = AllowedBlockList[4][PropDictS1[BlockIndex]['BlockType']]
                                            #checking for input ports.
                                            PortName = 'Input'
                                            NumberOfInputPorts = ports[0]
                                            self.NoUnconnectedBlocksUtil(PropDictS2,NameOfBlock,PortName,NumberOfInputPorts,PropDictS1[BlockIndex]['BlockType'],self.ModuleName,Rule_Id,Name,'DstBlock','SrcBlock')

                                            #checking for output ports
                                            PortName = 'Output'
                                            NumberOfOutputtPorts = ports[1]
                                            self.NoUnconnectedBlocksUtil(PropDictS2,NameOfBlock,PortName,NumberOfOutputtPorts,PropDictS1[BlockIndex]['BlockType'],self.ModuleName,Rule_Id,Name,'SrcBlock','DstBlock')
                                    else:
                                        #Here Checking wether DiscreteIntegrator is connected or not.
                                        if PropDictS1[BlockIndex]['BlockType'] in  AllowedBlockList[6]:
                                            if 'Name' in PropDictS1[BlockIndex].keys():
                                                NameOfBlock = PropDictS1[BlockIndex]['Name']
                                                if 'Ports' in PropDictS1[BlockIndex].keys():
                                                    Prts = PropDictS1[BlockIndex]['Ports']
                                                    if len(Prts) == 2:
                                                        #checking for input ports.
                                                        PortName = 'Input'
                                                        NumberOfInputPorts = Prts[0]
                                                        self.NoUnconnectedBlocksUtil(PropDictS2,NameOfBlock,PortName,NumberOfInputPorts,PropDictS1[BlockIndex]['BlockType'],self.ModuleName,Rule_Id,Name,'DstBlock','SrcBlock')

                                                        #checking for output ports
                                                        PortName = 'Output'
                                                        NumberOfOutputtPorts = Prts[1]
                                                        self.NoUnconnectedBlocksUtil(PropDictS2,NameOfBlock,PortName,NumberOfOutputtPorts,PropDictS1[BlockIndex]['BlockType'],self.ModuleName,Rule_Id,Name,'SrcBlock','DstBlock')
                                                    else:
                                                        if len(Prts) == 5:
                                                            #checking for input ports.
                                                            PortName = 'Input'
                                                            NumberOfInputPorts = Prts[0]
                                                            self.NoUnconnectedBlocksUtil(PropDictS2,NameOfBlock,PortName,NumberOfInputPorts,PropDictS1[BlockIndex]['BlockType'],self.ModuleName,Rule_Id,Name,'DstBlock','SrcBlock')

                                                            #checking for output ports
                                                            PortName = 'Output'
                                                            NumberOfOutputtPorts = Prts[1]+Prts[4]
                                                            self.NoUnconnectedBlocksUtil(PropDictS2,NameOfBlock,PortName,NumberOfOutputtPorts,PropDictS1[BlockIndex]['BlockType'],self.ModuleName,Rule_Id,Name,'SrcBlock','DstBlock')


                inpLst, foundLst, Name = self._getNextList()

    		# Checking wether SubSystems are connected or not and also check Wether subSystems have a redundent names or not
			# if SubSystems have a redundent Names add their ports.
            if len(SubSystemPrptyInfo1D)>0:
                SubSystemInfo = self.RemoveDuplicateNameUtil(SubSystemPrptyInfo1D)
                for SrckKey in range(0,len(SubSystemInfo)):
                    self.NoUnconnectedBlocksUtil(LineInfoOfModel,SubSystemInfo[SrckKey]['Name'],'Input',SubSystemInfo[SrckKey]['Ports'][0],'SubSystem',self.ModuleName,Rule_Id,SubSystemInfo[SrckKey]['SubSystemName'],'DstBlock','SrcBlock')

            if len(SubSystemPrptyInfo2D)>0:
                SubSystemInfo = self.RemoveDuplicateNameUtil(SubSystemPrptyInfo2D)
                for SrckKey in range(0,len(SubSystemInfo)):
                    self.NoUnconnectedBlocksUtil(LineInfoOfModel,SubSystemInfo[SrckKey]['Name'],'Input',SubSystemInfo[SrckKey]['Ports'][0],'SubSystem',self.ModuleName,Rule_Id,SubSystemInfo[SrckKey]['SubSystemName'],'DstBlock','SrcBlock')
                    self.NoUnconnectedBlocksUtil(LineInfoOfModel,SubSystemInfo[SrckKey]['Name'],'Output',SubSystemInfo[SrckKey]['Ports'][1],'SubSystem',self.ModuleName,Rule_Id,SubSystemInfo[SrckKey]['SubSystemName'],'SrcBlock','DstBlock')

            if len(SubSystemPrptyInfo4D)>0:
                SubSystemInfo = self.RemoveDuplicateNameUtil(SubSystemPrptyInfo4D)
                for SrckKey in range(0,len(SubSystemInfo)):
                    inputs = SubSystemInfo[SrckKey]['Ports'][0] + SubSystemInfo[SrckKey]['Ports'][3]
                    outputs = SubSystemInfo[SrckKey]['Ports'][1]
                    self.NoUnconnectedBlocksUtil(LineInfoOfModel,SubSystemInfo[SrckKey]['Name'],'Input',inputs,'SubSystem',self.ModuleName,Rule_Id,SubSystemInfo[SrckKey]['SubSystemName'],'DstBlock','SrcBlock')
                    self.NoUnconnectedBlocksUtil(LineInfoOfModel,SubSystemInfo[SrckKey]['Name'],'Output',outputs,'SubSystem',self.ModuleName,Rule_Id,SubSystemInfo[SrckKey]['SubSystemName'],'SrcBlock','DstBlock')
            if len(SubSystemPrptyInfo8D)>0:
                SubSystemInfo = self.RemoveDuplicateNameUtil(SubSystemPrptyInfo8D)
                for SrckKey in range(0,len(SubSystemInfo)):
                    inputs = SubSystemInfo[SrckKey]['Ports'][0] + SubSystemInfo[SrckKey]['Ports'][7]
                    outputs = SubSystemInfo[SrckKey]['Ports'][1]
                    self.NoUnconnectedBlocksUtil(LineInfoOfModel,SubSystemInfo[SrckKey]['Name'],'Input',inputs,'SubSystem',self.ModuleName,Rule_Id,SubSystemInfo[SrckKey]['SubSystemName'],'DstBlock','SrcBlock')
                    self.NoUnconnectedBlocksUtil(LineInfoOfModel,SubSystemInfo[SrckKey]['Name'],'Output',outputs,'SubSystem',self.ModuleName,Rule_Id,SubSystemInfo[SrckKey]['SubSystemName'],'SrcBlock','DstBlock')

        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_Id, 'Rule Check is excluded in this Module')

    #------------------------------------------------------------------------------------------
    def checkPrtyShouldExist_RCAPI(self,Rule_ID,PropName,SrchKeys):
        '''
         DocBlock should exist in every model file at root level
        '''
        SubSystmNames,SubSystemPrptyInfo1D,SubSystmPrptyInfo2D,LineInfoOfMdl,SubSystmPrptyInfo4D,SubSystmPrptyInfo8D,RootLevelSystemInfo=self.SubSystemNamesUtil()
        inpLst = RootLevelSystemInfo['List']
        GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst, 'Block', SrchKeys)
        ResultCount=0
        for BlockIndex in range(0,len(PropDictS1)):
            if 'BlockType' in PropDictS1[BlockIndex].keys():
                if 'SourceType' in PropDictS1[BlockIndex].keys():
                    if PropDictS1[BlockIndex]['SourceType'] == 'DocBlock':
                        if 'ECoderFlag' in PropDictS1[BlockIndex].keys():
                            if PropDictS1[BlockIndex]['ECoderFlag'] == PropName:
                                ResultCount = ResultCount+1
        if ResultCount >0:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                Rule_ID, 'DocBlock of Type /"'+PropName+'" exist at root Level')
        else:
            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                Rule_ID, 'DocBlock \"'+PropName+'" not exist at root Level with name of \"'+PropName+'"')
    #------------------------------------------------------------------------------------------
    '''
	    This utility used to removing the duplicate Names of subSystems
	'''
    def RemoveDuplicateNameUtil(self,SubSystemPrptyInfo):
        if  len(SubSystemPrptyInfo)>0:
            for SubSystemsIndex in range(0,len(SubSystemPrptyInfo)):
                if len(SubSystemPrptyInfo)>SubSystemsIndex:
                    if len(SubSystemPrptyInfo[SubSystemsIndex]['Ports']) == 2:
                        ports = []
                        for SearchIndex in range(SubSystemsIndex+1,len(SubSystemPrptyInfo)):
                            if len(SubSystemPrptyInfo)>SearchIndex:
                                if SubSystemPrptyInfo[SubSystemsIndex]['Name'] == SubSystemPrptyInfo[SearchIndex]['Name']:
                                    ports1 = SubSystemPrptyInfo[SubSystemsIndex]['Ports'][0]
                                    ports2 = SubSystemPrptyInfo[SearchIndex]['Ports'][0]
                                    ports.append(ports1+ports2)
                                    ports1 = SubSystemPrptyInfo[SubSystemsIndex]['Ports'][1]
                                    ports2 = SubSystemPrptyInfo[SearchIndex]['Ports'][1]
                                    ports.append(ports1+ports2)
                                    SubSystemPrptyInfo[SubSystemsIndex]['Ports'] = ports
                                    SubSystemPrptyInfo.pop(SearchIndex)

                    else:
                        if len(SubSystemPrptyInfo[SubSystemsIndex]['Ports']) == 4:
                            ports = []
                            for SearchIndex in range(SubSystemsIndex+1,len(SubSystemPrptyInfo)):
                                if len(SubSystemPrptyInfo)>SearchIndex:
                                    if SubSystemPrptyInfo[SubSystemsIndex]['Name'] == SubSystemPrptyInfo[SearchIndex]['Name']:
                                        ports1 = SubSystemPrptyInfo[SubSystemsIndex]['Ports'][0]
                                        ports2 = SubSystemPrptyInfo[SearchIndex]['Ports'][0]
                                        ports.append(ports1+ports2)

                                        ports1 = SubSystemPrptyInfo[SubSystemsIndex]['Ports'][1]
                                        ports2 = SubSystemPrptyInfo[SearchIndex]['Ports'][1]
                                        ports.append(ports1+ports2)

                                        ports1 = SubSystemPrptyInfo[SubSystemsIndex]['Ports'][2]
                                        ports2 = SubSystemPrptyInfo[SearchIndex]['Ports'][2]
                                        ports.append(ports1+ports2)

                                        ports1 = SubSystemPrptyInfo[SubSystemsIndex]['Ports'][3]
                                        ports2 = SubSystemPrptyInfo[SearchIndex]['Ports'][3]
                                        ports.append(ports1+ports2)
                                        SubSystemPrptyInfo[SubSystemsIndex]['Ports'] = ports
                                        SubSystemPrptyInfo.pop(SearchIndex)
                        else:
                            if len(SubSystemPrptyInfo[SubSystemsIndex]['Ports']) == 8:
                                ports = []
                                for SearchIndex in range(SubSystemsIndex+1,len(SubSystemPrptyInfo)):
                                    if len(SubSystemPrptyInfo)>SearchIndex:
                                       if SubSystemPrptyInfo[SubSystemsIndex]['Name'] == SubSystemPrptyInfo[SearchIndex]['Name']:
                                            ports1 = SubSystemPrptyInfo[SubSystemsIndex]['Ports'][0]
                                            ports2 = SubSystemPrptyInfo[SearchIndex]['Ports'][0]
                                            ports.append(ports1+ports2)

                                            ports1 = SubSystemPrptyInfo[SubSystemsIndex]['Ports'][1]
                                            ports2 = SubSystemPrptyInfo[SearchIndex]['Ports'][1]
                                            ports.append(ports1+ports2)

                                            ports.append(0)
                                            ports.append(0)
                                            ports.append(0)
                                            ports.append(0)
                                            ports.append(0)

                                            ports1 = SubSystemPrptyInfo[SubSystemsIndex]['Ports'][7]
                                            ports2 = SubSystemPrptyInfo[SearchIndex]['Ports'][7]
                                            ports.append(ports1+ports2)
                                            SubSystemPrptyInfo[SubSystemsIndex]['Ports'] = ports
                                            SubSystemPrptyInfo.pop(SearchIndex)

                else:
                    break
        return 	SubSystemPrptyInfo


    #-------------------------------------------------------------------------------------------

    '''
      Here check wether Blocks are connected with Lines or not
    '''
    def NoUnconnectedBlocksUtil(self,LineData,BlockName,NameOfPort,NoOfports,BlockTypeName,moduleName,RId,NameOfSystem,PrptyExist1,PrptyExist2):
        PortsCounter = 0
        for LineIndex in range(0,len(LineData)):
            #check wether the LineBlockType('SrcBlock' or 'DstBlock') is available in the Line block or not.
            if PrptyExist1 in LineData[LineIndex].keys():
                #check wether Name of the SrcBlock  or DstBlock is matching with the Block Name.
                if  BlockName == LineData[LineIndex][PrptyExist1] and PrptyExist2 in LineData[LineIndex].keys():
                    PortsCounter = PortsCounter+1
        if PortsCounter >= NoOfports:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", moduleName,
                 RId, 'BlcokType :\"'+BlockTypeName+'" of Name:\"'+BlockName+'"\, all \"'+NameOfPort+'" ports has connected in \"'+NameOfSystem+'"')
        else:
            if NameOfPort == 'Input':
                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", moduleName,
                     RId,'Unused Inpts should be connected to Ground in BlockType:\"'+BlockTypeName+'"of Name:\"'+BlockName+'" in \"'+NameOfSystem+'"' )
            else:
                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", moduleName,
                     RId, 'Unused Outputs should be connected to Terminator in BlockType:\"'+BlockTypeName+'"of Name:\"'+BlockName+'" in \"'+NameOfSystem+'"')


    #-------------------------------------------------------------------------------------------
    def checkBlockOutputType_RCAPI(self,RULE_ID, srchKeys, blockType,ExceptionModule = []):
        '''
            In each block check for receiving argument "blockType" property.
            If that BlockType maches with that property then Check for OutDataTypeStr property in
            same block,if the value is boolean then say pass.also it is checking
			for inherit property in if self.BoolPrtyData['BooleanDataType'].
        '''
        if self.ModuleName not in ExceptionModule:
       	    inpLst, foundLst, Name = self._getNextList()
            while (foundLst == True):
                #get the Block and Line data with SearchKeys.
                GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Block', srchKeys)
                for srchIndex in range(0,len(PropDictS1)):
                    if PropDictS1[srchIndex]['BlockType'] == blockType:
                        if 'OutDataTypeStr' in PropDictS1[srchIndex].keys():
                            if PropDictS1[srchIndex]['OutDataTypeStr'] == 'boolean':
                                self.dataLoggerObj.logCondResult("-","-","PASS","::",self.ModuleName,RULE_ID,'the output data type of the \"'+blockType+'":\"'+PropDictS1[srchIndex]['Name']+'" is boolean in \"'+Name+'"')
                            else:
                                ValueOfOutDataType = PropDictS1[srchIndex]['OutDataTypeStr']
                                if '(' in ValueOfOutDataType:
                                    subLst = ValueOfOutDataType.split('(')
                                    if 'boolean' in subLst[1] and 'DataTypeOverride' in subLst[1] and 'Off' in subLst[1]:
                                        self.dataLoggerObj.logCondResult("-","-","PASS","::",self.ModuleName,RULE_ID,'the output data type of the \"'+blockType+'":\"'+PropDictS1[srchIndex]['Name']+'" is boolean in \"'+Name+'"')
                                    else:
                                        self.dataLoggerObj.logCondResult("-","-","FAIL","::",self.ModuleName,RULE_ID,'The output data type of the \"'+blockType+'" : \"'+PropDictS1[srchIndex]['Name']+'"should be Boolean type in \"'+Name+'".')
                                else:
                                    self.dataLoggerObj.logCondResult("-","-","FAIL","::",self.ModuleName,RULE_ID,'The output data type of the \"'+blockType+'" : \"'+PropDictS1[srchIndex]['Name']+'"should be Boolean type in \"'+Name+'".')
                        else:
                            if 'BooleanDataType' in self.BoolPrtyData.keys():
                                if self.BoolPrtyData['BooleanDataType'] == 'on':
                                    self.dataLoggerObj.logCondResult("-","-","PASS","::",self.ModuleName,RULE_ID,'the output data type of the \"'+blockType+'":\"'+PropDictS1[srchIndex]['Name']+'" is boolean in \"'+Name+'"')
                                else:
                                    self.dataLoggerObj.logCondResult("-","-","FAIL","::",self.ModuleName,RULE_ID,'The output data type of the \"'+blockType+'" : \"'+PropDictS1[srchIndex]['Name']+'"should be Boolean type in \"'+Name+'".')
                inpLst, foundLst, Name = self._getNextList()
        else:
 		    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

    #---------------------------------------------------------------------------------------------
    def SubSystemNamesUtil(self):

        #note down all subSystem Names into SubSystemNamesList.
        SubSystemNamesList = []
        SubSystemsPropList = []
        SubSystemsPropList1D = []
        SubSystemsPropList2D = []
        SubSystemsPropList4D = []
        SubSystemsPropList8D = []
        RootLevelSystmInfo = {}
        LineInfoOfModel    = []
        Names = {}
        SubSystemProperties = {}
        inpLstSub, foundLstBool, NameOfSubSystem = self._getNextList()
        while foundLstBool == True:
            RootLevelSystmInfo = {}
            RootLevelSystmInfo = inpLstSub
            Names['BlockType'] ='SubSystem'
            Names['Name'] = NameOfSubSystem
            SubSystemNamesList.append(Names)
            Names = {}
			#get all AllSubSystems [Name,Ports].
            GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLstSub['List'], 'Block', ['BlockType','Name','Ports'])
            GetStatsS2, PropDictS2, rSubLstS2, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLstSub['List'], 'Line', ['SrcBlock','DstBlock','Name','DstPort','SrcPort'])
            LineInfoOfModel=LineInfoOfModel + PropDictS2
            if len(PropDictS1)>0:
                if 'BlockType' in PropDictS1[0].keys() :
                    if PropDictS1[0]['BlockType'] == 'SubSystem':
                        SubSystemProperties['Name'] = PropDictS1[0]['Name']
                        SubSystemProperties['SubSystemName'] = NameOfSubSystem
                        if 'Ports' in PropDictS1[0].keys():
                            #2D Ports
                            if len(PropDictS1[0]['Ports']) == 1:
                                SubSystemProperties['Ports'] = PropDictS1[0]['Ports']
                                SubSystemsPropList1D.append(SubSystemProperties)

                            if len(PropDictS1[0]['Ports']) == 2:
                                SubSystemProperties['Ports'] = PropDictS1[0]['Ports']
                                SubSystemsPropList2D.append(SubSystemProperties)
                            else:
                                if len(PropDictS1[0]['Ports']) == 4:
                                    SubSystemProperties['Ports'] = PropDictS1[0]['Ports']
                                    SubSystemsPropList4D.append(SubSystemProperties)
                                else:
                                    if len(PropDictS1[0]['Ports']) == 8:
                                        SubSystemProperties['Ports'] = PropDictS1[0]['Ports']
                                        SubSystemsPropList8D.append(SubSystemProperties)

            SubSystemProperties = {}

            inpLstSub, foundLstBool, NameOfSubSystem = self._getNextList()
		#remove Main SystemName
        SubSystemNamesList = SubSystemNamesList[0:len(SubSystemNamesList)-1]

        #SubSystemNamesList:It contains Names of all subSystems
        #SubSystemsPropList2D,4D,8D:It contains [Name,Ports] of all 2D ports-SubSystems.
        #LineInfoOfModel   :It contains Line information of Model file.

        return  SubSystemNamesList,SubSystemsPropList1D,SubSystemsPropList2D,LineInfoOfModel,SubSystemsPropList4D,SubSystemsPropList8D,RootLevelSystmInfo

    #--------------------------------------------------------------------------------------

    def checkTagNameAndSignalOrBusMustMatch_RCAPI(self, Rule_ID, PropChkData, UniqueKey, CheckType,AllowedBlocks,ExceptionModule = []):
        '''
		Misra 18B:
		          first take the values of [gotoTag,Name] properties from GOTO and FROM blocks.similerly extract [srcBlock,Name]
				  From Line block and [dstBlock,Name] from Line block individually then start comparing the FROM or GOTO tag name
				  and Signal name or bus name.
        '''
        if self.ModuleName not in ExceptionModule:
            srchKeysS1 = []
            srchKeysS1+=UniqueKey
            srchKeysS1.append(PropChkData['SourceProp'])
            srchKeysS1 = list(set(srchKeysS1))

            if CheckType == 'Exist':
                SubSystemNames,PortDataOf1D,SubSystemPrpInfo,LineInfo,PortDataOf4D,PortDataOf8D,SystemInfo = self.SubSystemNamesUtil()

            inpLst, foundLst, Name = self._getNextList()
            while (foundLst == True):
                GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Block', srchKeysS1)
                GetStatsS2, PropDictS2, rSubLstS2, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Line', ['SrcBlock','DstBlock','Name'])
                if CheckType == 'Exact':

                    ListForFrom = []
                    ListForGoto = []
                    #retrieve [Gototag,Name ] property values from Block of BlockType From and Goto
                    for searchItem in range(0,len(GetStatsS1)):
                        if GetStatsS1[searchItem] == 1:
					        #check wether Blocktype is available in PropDictS1 at selected index.
                            if UniqueKey[0] in PropDictS1[searchItem].keys():
                                #compare BlockType for From
                                if PropDictS1[searchItem][UniqueKey[0]] == PropChkData['SourceBlockType']:
							        #check for gototag available in propDict
                                    if PropChkData['SourceProp'] in PropDictS1[searchItem].keys():
								        #take the value of gototag from From
                                        SourceProp = PropDictS1[searchItem][PropChkData['SourceProp']]
									    #read the Name property if BlockType==From
                                        if 'Name' in PropDictS1[searchItem]:
                                            SourceName = PropDictS1[searchItem]['Name']
                                            #ListForFrom holds the values of Block type Goto of [GotoTag property value,Name property value]
                                            ListForFrom.append([SourceProp,SourceName])
                                        else:
                                            SourceName = '<Unknown>'
                                            ListForFrom.append([SourceProp,SourceName])

                            if UniqueKey[0] in PropDictS1[searchItem].keys():
                                if PropDictS1[searchItem][UniqueKey[0]] == PropChkData['DestBlockType']:
                                    if PropChkData['DestProp'] in PropDictS1[searchItem].keys():
                                        ValueOfGotoTag = PropDictS1[searchItem][PropChkData['DestProp']]
                                        if 'Name' in PropDictS1[searchItem]:
                                            SourceName = PropDictS1[searchItem]['Name']
                                            ListForGoto.append([ValueOfGotoTag,SourceName])
                                        else:
                                            SourceName = '<Unknown>'
                                            ListForGoto.append([ValueOfGotoTag,SourceName])


				    # This code compares the GotoTag property and Signal or Bus Name in FROM and GOTO Properties.
                    if len(ListForFrom)>0 and len(ListForGoto)>0:
                        #search for signal or bus name which is going out from the FROM block is matching with the FROM block Name or not
                        for SrchItem in range(0,len(ListForFrom)):
                                ResultType	= 0
                                matchCase1  = 0
                                matchCase2  = 0
                                for SrchItem2 in range(0,len(GetStatsS2)):
                                    if 'SrcBlock' in PropDictS2[SrchItem].keys():
                                        if str(PropDictS2[SrchItem2]['SrcBlock']) == (ListForFrom[SrchItem][1]):
                                            #note the positions where FromTag and its Signal matches
                                            matchCase1 = SrchItem
                                            matchCase2 = SrchItem2
                                            ResultType = 1
                                            break
                                if ResultType == 0:
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                         Rule_ID,'No Signal From FROM Block of  SourceBlock type \"'+PropDictS2[SrchItem]['SrcBlock'])
                                else:
                                    if ResultType == 1:
                                        if 'Name' in PropDictS2[matchCase2].keys():
										   #compare signal or bus name and FROM block name.
                                            labelName = PropDictS2[matchCase2]['Name']
                                            if '<' in labelName and '>' in labelName:											 
                                                if labelName[0] == '<' and labelName[len(labelName)-1] == '>':
                                                    if labelName[1:len(labelName)-1] ==  ListForFrom[matchCase1][0]:
                                                        self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                             Rule_ID, 'FROM Block of TagName:\"'+ListForFrom[matchCase1][0]+'" and its Signal Name\"'+PropDictS2[matchCase2]['Name']+'" matched in \"'+Name+'".')
                                                    else:
                                                        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                             Rule_ID, 'FROM Block of TagName:\"'+ListForFrom[matchCase1][0]+'" and its Signal Name\"'+PropDictS2[matchCase2]['Name']+'" mis-matched in \"'+Name+'".')
                                            else:
                                                if PropDictS2[matchCase2]['Name'] ==  ListForFrom[matchCase1][0]:
                                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                         Rule_ID, 'FROM Block of TagName:\"'+ListForFrom[matchCase1][0]+'" and its Signal Name\"'+PropDictS2[matchCase2]['Name']+'" matched in \"'+Name+'".')
                                                else:
                                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                         Rule_ID, 'FROM Block of TagName:\"'+ListForFrom[matchCase1][0]+'" and its Signal Name\"'+PropDictS2[matchCase2]['Name']+'" mis-matched in \"'+Name+'".')
											
                                        else:
                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                 Rule_ID, 'signal does not have lable string from FROM Block of TagName:\"'+ListForFrom[matchCase1][0]+'" in \"'+Name+'".')
                        #search for signal or bus name which is coming to GOTO block is matching with the GOTO block Name or not
                        for SrchItem in range(0,len(ListForGoto)):
                                ResultType	= 0
                                matchCase1  = 0
                                matchCase2  = 0
                                for SrchItem2 in range(0,len(GetStatsS2)):
                                    if 'DstBlock' in PropDictS2[SrchItem2].keys():
                                        if str(PropDictS2[SrchItem2]['DstBlock']) == (ListForGoto[SrchItem][1]):
                                           #note the positions where FromTag and its Signal matches
                                            matchCase1 = SrchItem
                                            matchCase2 = SrchItem2
                                            ResultType = 1
                                            break
                                if ResultType == 0:
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                         Rule_ID,'No Signal is coming for GOTO Block in \"'+Name+'".')
                                else:
                                    if ResultType == 1:
                                        if 'Name' in PropDictS2[matchCase2].keys():
                                            labelName = PropDictS2[matchCase2]['Name']
                                            if '<' in labelName and '>' in labelName:											 
                                                if labelName[0] == '<' and labelName[len(labelName)-1] == '>':
                                                #compare signal or bus name and FROM block name.
                                                    if labelName[1:len(labelName)-1] ==  ListForGoto[matchCase1][0]:
                                                        self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                             Rule_ID, 'GOTO Block of TagName:\"'+ListForGoto[matchCase1][0]+'" and its Signal Name\"'+PropDictS2[matchCase2]['Name']+'" matched in \"'+Name+'".')
                                                    else:
                                                        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                             Rule_ID, 'GOTO Block of TagName:\"'+ListForGoto[matchCase1][0]+'" and its Signal Name\"'+PropDictS2[matchCase2]['Name']+'" mis-matched in \"'+Name+'".')
                                            else:
                                                if PropDictS2[matchCase2]['Name'] ==  ListForGoto[matchCase1][0]:
                                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                         Rule_ID, 'GOTO Block of TagName:\"'+ListForGoto[matchCase1][0]+'" and its Signal Name\"'+PropDictS2[matchCase2]['Name']+'" matched in \"'+Name+'".')
                                                else:
                                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                         Rule_ID, 'GOTO Block of TagName:\"'+ListForGoto[matchCase1][0]+'" and its Signal Name\"'+PropDictS2[matchCase2]['Name']+'" mis-matched in \"'+Name+'".')
											
                                        else:
                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                 Rule_ID, 'signal does not have lable string for GOTO Block of TagName:\"'+ListForGoto[matchCase1][0]+'" in \"'+Name+'".')
                else:
                    if CheckType == 'Exist':
                        status = 0
                        GetStatsS3, PropDictS3, rSubLstS3, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__SFlist, 'chart', ['name'])
                        if len(GetStatsS3)>0:
                            if len(PropDictS1):
                               if 'BlockType' in PropDictS1[0].keys():
                                    for StateIndex in range(0,len(PropDictS3)):
                                        if PropDictS1[0][UniqueKey[0]] == 'SubSystem' and  PropDictS1[0]['Name'] == PropDictS3[StateIndex]['name']:
                                            status = 1

						#if you have any Stetflow,then no need go and check inside the statechart.this rule applicable only for simulink and subSystem.
                        if status == 0:
                            ##check the rule for destination block type GOTO,MUX,BUSCreator.
                            for BlockIndex in range(0,len(PropDictS1)):
                                #check 'BlockType' is available in BlockData.
                                if UniqueKey[0] in PropDictS1[BlockIndex].keys():
                                    #check wether BlockType is matching with any AllowedBlocks
                                    if PropDictS1[BlockIndex][UniqueKey[0]] in AllowedBlocks:
                                        for LineIndex in  range(0,len(PropDictS2)):
                                            #check wether Line Block contains the 'DstBlock' or not
                                            if PropChkData['BlockProp'] in  PropDictS2[LineIndex].keys():
                                                #if DstBlock name in Line and AllowedBlock name matching or not
                                                if PropDictS2[LineIndex][PropChkData['BlockProp']] == PropDictS1[BlockIndex]['Name']:
                                                    #if Name is available then it shouldn't be empty
                                                    if 'RP_0064' == Rule_ID:
                                                        if 'Name' in PropDictS2[LineIndex].keys():
                                                            nameOfLine = PropDictS2[LineIndex]['Name']
                                                            if '<' in nameOfLine and '>' in nameOfLine:
                                                                if nameOfLine[0] == '<' and nameOfLine[len(nameOfLine)-1] == '>':
                                                                   self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                                         Rule_ID,'Output Line name of Block:\"'+PropDictS1[BlockIndex]['Name']+'" is labelled with Propagated label:\"'+nameOfLine+'" in \"'+Name+'"')
                                                                else:
                                                                   self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                         Rule_ID,'Give proper output Line name from the Block:\"'+PropDictS1[BlockIndex]['Name']+'" in \"'+Name+'"')
                                                            else:
                                                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                     Rule_ID,'All signal or Bus originating from Block:\"'+PropDictS1[BlockIndex]['Name']+'" Must be labelled with propagated labels in \"'+Name+'"')
                                                        else:
                                                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                     Rule_ID,'All signal or Bus originating from Block:\"'+PropDictS1[BlockIndex]['Name']+'" Must be labelled with propagated labels in \"'+Name+'"')
                                                    else:
                                                        if 'Name' in PropDictS2[LineIndex].keys():
                                                            if len(PropDictS2[LineIndex]['Name'].split()) == 0:
                                                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                     Rule_ID, 'Signal or Bus name should not be empty in Line of \"'+PropChkData['BlockProp']+'" Type\"'+PropDictS2[LineIndex][PropChkData['BlockProp']]+'" in \"'+Name+'".')
                                                            else:
  	                                                            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                                     Rule_ID, 'Signal or Bus for \"'+PropChkData['BlockProp']+'" of \"'+PropDictS2[LineIndex][PropChkData['BlockProp']]+'" has lablled in \"'+Name+'".')
                                                        else:
                                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                 Rule_ID, 'Signal or Bus Name must be specify in Line of \"'+PropChkData['BlockProp']+'" is:\"'+PropDictS2[LineIndex][PropChkData['BlockProp']]+'" in \"'+Name+'".')                            #rule checking for signal or bus which is connecting to SusbSystem like StateChart,SubSystem.
                            for BlockIndex in range(0,len(SubSystemNames)):
                                if 'BlockType' in SubSystemNames[BlockIndex].keys():
                                    if SubSystemNames[BlockIndex]['BlockType'] == 'SubSystem':
                                        for LineIndex in  range(0,len(PropDictS2)):
                                            if PropChkData['BlockProp'] in  PropDictS2[LineIndex].keys():
                                                if PropDictS2[LineIndex][PropChkData['BlockProp']] == SubSystemNames[BlockIndex]['Name']:
                                                    if 'RP_0064' == Rule_ID:
                                                        if 'Name' in PropDictS2[LineIndex].keys():
                                                            nameOfLine = PropDictS2[LineIndex]['Name']
                                                            if '<' in nameOfLine and '>' in nameOfLine:
                                                                if nameOfLine[0] == '<' and nameOfLine[len(nameOfLine)-1] == '>':
                                                                   self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                                         Rule_ID,'Output Line name of Block:\"'+SubSystemNames[BlockIndex]['Name']+'" is labelled with Propagated label:\"'+nameOfLine+'" in \"'+Name+'"')
                                                                else:
                                                                   self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                         Rule_ID,'Give proper output Line name from the Block:\"'+SubSystemNames[BlockIndex]['Name']+'" in \"'+Name+'"')
                                                            else:
                                                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                     Rule_ID,'All signal or Bus originating from Block:\"'+SubSystemNames[BlockIndex]['Name']+'" Must be labelled with propagated labels in \"'+Name+'"')
                                                        else:
                                                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                     Rule_ID,'All signal or Bus originating from Block:\"'+SubSystemNames[BlockIndex]['Name']+'" Must be labelled with propagated labels in \"'+Name+'"')
                                                    else:
                                                        if 'Name' in PropDictS2[LineIndex].keys():
                                                            if len(PropDictS2[LineIndex]['Name'].split()) == 0:
                                                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                     Rule_ID, 'Signal or Bus name should not be empty in Line of \"'+PropChkData['BlockProp']+'" Type\"'+PropDictS2[LineIndex][PropChkData['BlockProp']]+'" in \"'+Name+'".')
                                                            else:
                                                                self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                                     Rule_ID, 'Signal or Bus for \"'+PropChkData['BlockProp']+'" of \"'+PropDictS2[LineIndex][PropChkData['BlockProp']]+'" has lablled in \"'+Name+'".')
                                                        else:
                                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                 Rule_ID, 'Signal or Bus Name must be specify in Line  of\"'+PropChkData['BlockProp']+'" :\"'+PropDictS2[LineIndex][PropChkData['BlockProp']]+'" in \"'+Name+'".')
                    elif CheckType == 'Match':
                        ThrldValue = []
                        ThrldValue = ['0.5']
                        for BlkIndex in range(0,len(PropDictS1)):
                            if 'BlockType' in PropDictS1[BlkIndex].keys():
                                if PropDictS1[BlkIndex]['BlockType'] == 'Switch':
                                    if 'Criteria' not in PropDictS1[BlkIndex].keys():
                                        if 'Threshold' not in PropDictS1[BlkIndex].keys():
                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                 Rule_ID, 'Threshold value shoun not be Zero for Switch Name\"'+PropDictS1[BlkIndex]['Name']+'" in \"'+Name+'".')
                                        else:
                                            if PropDictS1[BlkIndex]['Threshold'] == ThrldValue[0]:
                                                self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                     Rule_ID, 'Threshold value 0.5 is allowed in Switch Block of Name:\"'+PropDictS1[BlkIndex]['Name']+'" in \"'+Name+'".')
                                            else:
                                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                     Rule_ID, 'Threshold value\"'+PropDictS1[BlkIndex]['Threshold']+'" is not allowed in Switch Block of Name: \"'+PropDictS1[BlkIndex]['Name']+'" in \"'+Name+'".')
                    else:
                        if CheckType == 'Unique':
                            for searchPos in range(0,len(PropDictS1)):
                                if PropDictS1[searchPos]['BlockType'] == 'Merge':
                                    noOfinIputPorts = PropDictS1[searchPos]['Ports'][0]
                                    noOfOutputPorts = 1
                                    resultType = 0
                                    name = ''
                                    path = Name+'/'+PropDictS1[searchPos]['Name']
                                    for searchItem in range(0,len(GetStatsS2)):
                                        if 'SrcBlock' in PropDictS2[searchItem].keys():
                                            if PropDictS2[searchItem]['SrcBlock'] == PropDictS1[searchPos]['Name']:
                                                if 'Name' in PropDictS2[searchItem].keys():
                                                    name = PropDictS2[searchItem]['Name']
                                                    if '<' in name and '>' in name:
                                                        name = name[1:len(name)-1]
                                                    resultType = 1
                                    if resultType == 1:
                                        rcount = 0
                                        for srchIndx in range(0,len(PropDictS2)):
                                            if 'DstBlock' in PropDictS2[srchIndx].keys():
                                                if PropDictS2[srchIndx]['DstBlock'] == PropDictS1[searchPos]['Name']:
                                                    if 'Name' in PropDictS2[srchIndx].keys():
                                                        name2 = PropDictS2[srchIndx]['Name']
                                                        if '<' in name2 and '>' in name2:
                                                            name2 = name2[1:len(name2)-1]
                                                        if name2 == name:
                                                            rcount = rcount+1
                                        if rcount == noOfinIputPorts:
                                            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                Rule_ID, 'All signals entering and leaving a merge block have matching name in \"'+path+'".')
                                        else:
                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                Rule_ID, 'All signals entering and leaving a merge block has not matched in \"'+path+'".')

                                    else:
                                        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                            Rule_ID, 'All signals entering and leaving a merge block has not matched in \"'+path+'".')

                inpLst, foundLst, Name = self._getNextList()
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')
    #-------------------------------------------------------------------------------------------



    def checkBlckPropValueInOtherBlock_RCAPI(self, Rule_ID, PropChkData, UniqueKey, CheckType, ExceptionModule = []):
        '''
        In each block of the requested block type, search the property keyword and note down the values.
        Perform this for the second set of block type.
        If property keyword exists in the first set, compare its value with the second set property keyword values.
        '''
        if self.ModuleName not in ExceptionModule:
            srchKeysS1 = []
            srchKeysS2 = []
            srchKeysS1+=UniqueKey
            srchKeysS1.append(PropChkData['SourceProp'])
            srchKeysS1 = list(set(srchKeysS1))

            srchKeysS2+=UniqueKey
            srchKeysS2.append(PropChkData['DestProp'])
            srchKeysS2 = list(set(srchKeysS2))

            inpLst, foundLst, Name = self._getNextList()
            while (foundLst == True):
                GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Block', srchKeysS1)
                GetStatsS2, PropDictS2, rSubLstS2, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Block', srchKeysS2)

                #process only if something is found in the list.
                for searchItem in range(0,len(GetStatsS1)):
                    if GetStatsS1[searchItem] == 1:
                        if UniqueKey[0] in PropDictS1[searchItem].keys():
                            if PropDictS1[searchItem][UniqueKey[0]] == PropChkData['SourceBlockType']:
                                if PropChkData['SourceProp'] in PropDictS1[searchItem].keys():
                                    SourceProp = PropDictS1[searchItem][PropChkData['SourceProp']]
                                    if 'Name' in PropDictS1[searchItem]:
                                        SourceName = PropDictS1[searchItem]['Name']
                                    else:
                                        SourceName = '<Unknown>'

                                    SearchResult = 0
                                    for Destitem in range(0,len(GetStatsS2)):
                                        if GetStatsS2[Destitem] == 1:
                                            if UniqueKey[0] in PropDictS2[Destitem].keys():
                                                if PropDictS2[Destitem][UniqueKey[0]] == PropChkData['DestBlockType']:
                                                    if PropChkData['DestProp'] in PropDictS2[Destitem].keys():
                                                        DestProp = PropDictS2[Destitem][PropChkData['DestProp']]
                                                        if DestProp == SourceProp:
                                                            SearchResult += 1
                                    if CheckType == 'Exist':
                                        if  SearchResult > 0:
                                            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                 Rule_ID, 'System \"'+Name+'\", block \"'+SourceName+'\" of type \"'+PropChkData['SourceBlockType']+'\", Keyword: \"'+PropChkData['SourceProp']+'\" value \"'+SourceProp+'\" is found in other block of type \"'+PropChkData['DestBlockType']+ '\"')
                                        else:
                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                 Rule_ID, 'System \"'+Name+'\", block \"'+SourceName+'\" of type \"'+PropChkData['SourceBlockType']+'\", Keyword: \"'+PropChkData['SourceProp']+'\" value \"'+SourceProp+'\" is not found in other block of type \"'+PropChkData['DestBlockType']+ '\"')
                                    if CheckType == 'Unique':
                                        if  SearchResult == 1:
                                            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                 Rule_ID, 'System \"'+Name+'\", block \"'+SourceName+'\" of type \"'+PropChkData['SourceBlockType']+'\", Keyword: \"'+PropChkData['SourceProp']+'\" value \"'+SourceProp+'\" is found only once in other block of type \"'+PropChkData['DestBlockType']+ '\"')
                                        elif  SearchResult > 1:
                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                 Rule_ID, 'System \"'+Name+'\", block \"'+SourceName+'\" of type \"'+PropChkData['SourceBlockType']+'\", Keyword: \"'+PropChkData['SourceProp']+'\" value \"'+SourceProp+'\" is found more than one occurance in other block of type \"'+PropChkData['DestBlockType']+ '\"')
                                        else:
                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                 Rule_ID, 'System \"'+Name+'\", block \"'+SourceName+'\" of type \"'+PropChkData['SourceBlockType']+'\", Keyword: \"'+PropChkData['SourceProp']+'\" value \"'+SourceProp+'\" is not found in other block of type \"'+PropChkData['DestBlockType']+ '\"')
                inpLst, foundLst, Name = self._getNextList()

        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

    #-------------------------------------------------------------------------------------------

    def checkBlckPropValueInOtherSFBlock_RCAPI(self, Rule_ID, PropChkData, CheckType, ExceptionModule = []):
        '''
        In each block of the requested block type, search the property keyword and note down the values.
        Perform this for the second set of block type.
        If property keyword exists in the first set, compare its value with the second set property keyword values.
        '''
        if self.ModuleName not in ExceptionModule:
                srchKeysS1 = []
                srchKeysS2 = []
                srchKeysS1.append(PropChkData['SourceProp'])
                srchKeysS1 = list(set(srchKeysS1))
                srchKeysS2.append(PropChkData['DestProp'])
                srchKeysS2 = list(set(srchKeysS2))
                GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__SFlist, 'data', srchKeysS1)
                GetStatsS2, PropDictS2, rSubLstS2, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__SFlist, 'state', srchKeysS2)
                #process only if something is found in the list.
                for searchItem in range(0,len(GetStatsS1)):
                    if GetStatsS1[searchItem] == 1:
                        if PropChkData['SourceProp'] in PropDictS1[searchItem].keys():
                            SourceProp = PropDictS1[searchItem][PropChkData['SourceProp']]
                            SearchResult = 0
                            for Destitem in range(0,len(GetStatsS2)):
                                if GetStatsS2[Destitem] == 1:
                                    if PropChkData['DestProp'] in PropDictS2[Destitem].keys():
                                        DestProp = PropDictS2[Destitem][PropChkData['DestProp']]
                                        if DestProp == SourceProp:
                                            SearchResult += 1
                            if CheckType == 'Exist':
                                if  SearchResult > 0:
                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                         Rule_ID, 'block of type \"'+PropChkData['SourceBlockType']+'\", Keyword: \"'+PropChkData['SourceProp']+'\" value \"'+SourceProp+'\" is found in other block of type \"'+PropChkData['DestBlockType']+ '\"')
                                else:
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                         Rule_ID, 'block of type \"'+PropChkData['SourceBlockType']+'\", Keyword: \"'+PropChkData['SourceProp']+'\" value \"'+SourceProp+'\" is not found in other block of type \"'+PropChkData['DestBlockType']+ '\"')
                            if CheckType == 'Unique':
                                if  SearchResult == 1:
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                         Rule_ID, 'block of type \"'+PropChkData['SourceBlockType']+'\", Keyword: \"'+PropChkData['SourceProp']+'\" value \"'+SourceProp+'\" is found only once in other block of type \"'+PropChkData['DestBlockType']+ '\"')
                                elif  SearchResult > 1:
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                         Rule_ID, 'block of type \"'+PropChkData['SourceBlockType']+'\", Keyword: \"'+PropChkData['SourceProp']+'\" value \"'+SourceProp+'\" is found more than one occurance in other block of type \"'+PropChkData['DestBlockType']+ '\"')
                            else:
                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                     Rule_ID, 'block of type \"'+PropChkData['SourceBlockType']+'\", Keyword: \"'+PropChkData['SourceProp']+'\" value \"'+SourceProp+'\" is not found in other block of type \"'+PropChkData['DestBlockType']+ '\"')

        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

    #-------------------------------------------------------------------------------------------

    def checkForDuplicatePropInBlocks_RCAPI(self, Rule_ID, PropChkData, UniqueKey, ExceptionModule = []):
        if self.ModuleName not in ExceptionModule:
            srchKeysS1 = []
            srchKeysS1+=UniqueKey
            srchKeysS1.append(PropChkData['SourceProp'])
            srchKeysS1 = list(set(srchKeysS1))
            inpLst, foundLst, Name = self._getNextList()
            while (foundLst == True):
                GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Block', srchKeysS1)
                SourcePropList = []
                #process only if something is found in the list.
                for searchItem in range(0,len(GetStatsS1)):
                    if GetStatsS1[searchItem] == 1:
                        if UniqueKey[0] in PropDictS1[searchItem].keys():
                            if PropDictS1[searchItem][UniqueKey[0]] == PropChkData['SourceBlockType']:
                                if PropChkData['SourceProp'] in PropDictS1[searchItem].keys():
                                    SourceProp = PropDictS1[searchItem][PropChkData['SourceProp']]
                                    if SourceProp not in SourcePropList:
                                        self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                             Rule_ID, 'System \"'+Name+'\", block: \"'+PropChkData['SourceBlockType']+'\", Keyword: \"'+PropChkData['SourceProp']+'\" value \"'+SourceProp+'\" is not found in other block of type \"'+PropChkData['SourceBlockType']+ '\"')
                                    else:
                                        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                             Rule_ID, 'System \"'+Name+'\", block: \"'+PropChkData['SourceBlockType']+'\", Keyword: \"'+PropChkData['SourceProp']+'\" value \"'+SourceProp+'\" is found in other block of type \"'+PropChkData['SourceBlockType']+ '\"')
                                    SourcePropList.append(SourceProp)
                inpLst, foundLst, Name = self._getNextList()
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

    #-------------------------------------------------------------------------------------------

    def checkForDuplicatePropInLines_RCAPI(self, Rule_ID, PropChkData, ExceptionModule = []):
        if self.ModuleName not in ExceptionModule:
            srchKeysS1 = []
            LinkData = []
            srchKeysS1.append(PropChkData['SourceProp'])
            srchKeysS1 = list(set(srchKeysS1))
            inpLst, foundLst, Name = self._getNextList()
            SourcePropList = []
            while (foundLst == True):
                GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Line', srchKeysS1)
                Srcblk = inpLst['LinkData']
                #process only if something is found in the list.
                for searchItem in range(0,len(GetStatsS1)):
                    if GetStatsS1[searchItem] == 1:
                        if PropChkData['SourceProp'] in PropDictS1[searchItem].keys():
                            SourceProp = PropDictS1[searchItem][PropChkData['SourceProp']]
                            if 'SrcBlock' in Srcblk[searchItem]:							
                                if SourceProp not in SourcePropList:
                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                         Rule_ID, 'System \"'+Name+'\", block: \"'+PropChkData['SourceBlockType']+'\", Keyword: \"'+PropChkData['SourceProp']+'\" value \"'+SourceProp+'\" is not found in other block of type \"'+PropChkData['SourceBlockType']+ '\" with Source block \"'+str(Srcblk[searchItem]['SrcBlock'])+'"')
                                else:
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                         Rule_ID, 'System \"'+Name+'\", block: \"'+PropChkData['SourceBlockType']+'\", Keyword: \"'+PropChkData['SourceProp']+'\" value \"'+SourceProp+'\" is found in other block of type \"'+PropChkData['SourceBlockType']+ '\" with Source block \"'+str(Srcblk[searchItem]['SrcBlock'])+'"')
                                SourcePropList.append(SourceProp)
                inpLst, foundLst, Name = self._getNextList()
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

    #-------------------------------------------------------------------------------------------


    def checkForDuplicatePropInSFBlocks_RCAPI(self, Rule_ID, PropChkData, ExceptionModule = []):
        if self.ModuleName not in ExceptionModule:
            srchKeysS1 = []
            srchKeysS1.append(PropChkData['SourceProp'])
            srchKeysS1 = list(set(srchKeysS1))
            GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__SFlist, 'state', srchKeysS1)
            SourcePropList = []
            #process only if something is found in the list.
            for searchItem in range(0,len(GetStatsS1)):
                if GetStatsS1[searchItem] == 1:
                    if PropChkData['SourceProp'] in PropDictS1[searchItem].keys():
                        SourceProp = PropDictS1[searchItem][PropChkData['SourceProp']]
                        x = SourceProp.find('/')
                        if x != -1:
                            a = SourceProp.rpartition("/")
                            if a[1] == '/':
                                if a[0] not in SourcePropList:
                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                         Rule_ID, 'block: \"'+PropChkData['SourceBlockType']+'\", Keyword: \"'+PropChkData['SourceProp']+'\" Label \"'+a[0]+'\" is not found in other block of type \"'+PropChkData['SourceBlockType']+ '\"')
                                else:
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                         Rule_ID, 'block: \"'+PropChkData['SourceBlockType']+'\", Keyword: \"'+PropChkData['SourceProp']+'\" Label \"'+a[0]+'\" is found in other block of type \"'+PropChkData['SourceBlockType']+ '\"')
                                SourcePropList.append(a[0])
                        else:
                            if SourceProp not in SourcePropList:
                                self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                     Rule_ID, 'block: \"'+PropChkData['SourceBlockType']+'\", Keyword: \"'+PropChkData['SourceProp']+'\" Label \"'+SourceProp+'\" is not found in other block of type \"'+PropChkData['SourceBlockType']+ '\"')
                            else:
                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                     Rule_ID, 'block: \"'+PropChkData['SourceBlockType']+'\", Keyword: \"'+PropChkData['SourceProp']+'\" Label \"'+SourceProp+'\" is found in other block of type \"'+PropChkData['SourceBlockType']+ '\"')
                            SourcePropList.append(SourceProp)

        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

    #-------------------------------------------------------------------------------------------
    def checkDataItemInOtherSFBlocks_RCAPI(self, Rule_ID, PropChkData, ExceptionModule = []):

        if self.ModuleName not in ExceptionModule:
            srchKeysS1 = []
            srchKeysS2 = []
            SourcePropLst = []
            TransDataLst = []
            StateDataLst = []
            srchKeysS1.append(PropChkData['SourceProp'])
            srchKeysS1 = list(set(srchKeysS1))
            srchKeysS2.append(PropChkData['DestProp'])
            srchKeysS2 = list(set(srchKeysS2))
            GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__SFlist, 'data', srchKeysS1)
            GetStatsS2, PropDictS2, rSubLstS2, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__SFlist, 'state', srchKeysS2)
            GetStatsS3, PropDictS3, rSubLstS3, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__SFlist, 'transition', srchKeysS2)
            #process only if something is found in the list.
            for searchItem in range(0,len(GetStatsS1)):
                try:
                    SourceProp = PropDictS1[searchItem][PropChkData['SourceProp']]
                    SourcePropLst.append(SourceProp)
                except:
                    pass

            for srhItem in range(0,len(GetStatsS3)):
                try:
                    TransProp = PropDictS3[srhItem][PropChkData['DestProp']]
                    TransPropLst = []
                    TransPropLst.append(TransProp)
                   # removes special characters in str
                    TransPropLst1 = []
                    for item in TransPropLst:
                        item = re.split(r"[=]+|[\/]+|[*]+|[--]+|[++]+|[+]+|[-]+|[!]+|[,]+|[~]+|[%]+|[\^]+|[\|]+|[&]+|[\|\|]+|[&&]+|[']+|[>]+|[<]+|[>=]+|[<=]+|[==]+|[ ]+|[\[\]]+|[\(\)]", item)
                        TransPropLst1+=item
                    # removes the ';'
                    TransPropLst2 = []
                    TransPropLst3 = []
                    for j in range(0,len(TransPropLst1)):
                        if ';' in TransPropLst1[j]:
                            tp=TransPropLst1[j].partition(';')
                            TransPropLst2.append(list(tp[:-2])[0])
                        else:
                            TransPropLst2.append(TransPropLst1[j])

                    # removes space
                    le=len(TransPropLst1)
                    for i in range(0,le):
                        j=len(TransPropLst2[i].split())
                        if j != 0 :
                            TransPropLst3.append(TransPropLst2[i])
                    # removes keywords like if, else and elif
                    dataList = []
                    for item in TransPropLst3:
                        item = re.sub('if' , '', item)
                        item = re.sub('else', '', item)
                        item = re.sub('elif', '', item)
                        dataList.append(item)

                    TransDataLst=TransDataLst+dataList
                except:
                    pass

            for Destitem in range(0,len(GetStatsS2)):
                try:
                    StateProp = PropDictS2[Destitem][PropChkData['DestProp']]
                    StatePropLst3 = []
                    x = StateProp.find('/')
                    if x != -1:
                        StatePropLst = re.split(r"[\/]", StateProp)
                        StatePropLst1 = StatePropLst[1]
                        StatePropLst2 = re.split(r"[\\]"+"['n']", StatePropLst1)
                        if StatePropLst2[1].find(':') != -1:
                            lst_index = 2
                        else:
                            lst_index = 1
                        StatePropLst3 = StatePropLst2[lst_index:]
                    else:
                        try:
                            StatePropLst2 = re.split(r"[\\]"+"['n']", Destitem)
                            if StatePropLst2[1].find(':') != -1:
                                lst_index = 1
                            else:
                                lst_index = 0
                            StatePropLst3 = StatePropLst2[lst_index:]
                        except:
                            StatePropLst3.append(Destitem)
                    # removes special characters in str
                    StatePropLst4 = []
                    for item in StatePropLst3:
                        item = re.split(r"[=]+|[\/]+|[*]+|[--]+|[++]+|[+]+|[-]+|[!]+|[,]+|[~]+|[%]+|[\^]+|[\|]+|[&]+|[\|\|]+|[&&]+|[']+|[>]+|[<]+|[>=]+|[<=]+|[==]+|[ ]+|[\[\]]+|[\(\)]", item)
                        StatePropLst4+=item
                    # removes the ';'
                    StatePropLst5 = []
                    StatePropLst6 = []
                    for j in range(0,len(StatePropLst4)):
                        if ';' in StatePropLst4[j]:
                            tp=StatePropLst4[j].partition(';')
                            StatePropLst5.append(list(tp[:-2])[0])
                        else:
                            StatePropLst5.append(StatePropLst4[j])

                    # removes space
                    le=len(StatePropLst4)
                    for i in range(0,le):
                        j=len(StatePropLst5[i].split())
                        if j != 0 :
                            StatePropLst6.append(StatePropLst5[i])
                    # removes keywords like if, else and elif
                    dataList = []
                    for item in StatePropLst6:
                        item = re.sub('if' , '', item)
                        item = re.sub('else', '', item)
                        item = re.sub('elif', '', item)
                        dataList.append(item)

                    StateDataLst = StateDataLst+dataList
                except:
                    pass

            CompleteDataLst = StateDataLst+TransDataLst
            # checks if data items are present in complete data list.
            for item in SourcePropLst:
                if str(item) in CompleteDataLst:
                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                         Rule_ID, 'The data item \"'+str(item)+'" is used')
                else:
                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                         Rule_ID, 'The data item \"'+str(item)+'" is unused')

        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

    #-------------------------------------------------------------------------------------------
    def checkTemporalInOtherSFBlocks_RCAPI(self, Rule_ID, ChkItem, ExceptionModule = []):
        '''
        In each block of the requested block type, search the property keyword and note down the values.
        Perform this for the second set of block type.
        If property keyword exists in the first set, compare its value with the second set property keyword values.
        '''
        if self.ModuleName not in ExceptionModule:
            srchKeysS1 = ['id','name']
            srchKeysS2 = ['chart','labelString']
            StateLst = []
            TransitionLst = []
            StateDataLst = []
            GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__SFlist, 'chart', srchKeysS1)
            GetStatsS2, PropDictS2, rSubLstS2, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__SFlist, 'state', srchKeysS2)
            GetStatsS3, PropDictS3, rSubLstS3, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__SFlist, 'transition', srchKeysS2)
            for i in range(0,len(PropDictS1)):
                count = 0
                for j in range(0,len(PropDictS2)):
                    if( PropDictS2[j]['chart']==PropDictS1[i]['id']):
                        count=count+1
                        chartid = PropDictS1[i]['id']
                if count<2:
                    try:
                        for j in range(0,len(PropDictS2)):
                            if(PropDictS2[j]['chart']==chartid):
                                StateLst.append(PropDictS2[j]['labelString'])
                    except:
                        pass
                    for k in range(0,len(PropDictS3)):
                        if( PropDictS3[k]['chart']==PropDictS1[i]['id']):
                            try:
                                TransitionLst.append(PropDictS3[k]['labelString'])
                            except:
                                pass

            LabelStrLst = StateLst + TransitionLst
            for DestProp in LabelStrLst:
                try:
                    StatePropLst3 = []
                    x = DestProp.find('/')
                    if x != -1:
                        StatePropLst = re.split(r"[\/]", DestProp)
                        StatePropLst1 = StatePropLst[1]
                        StatePropLst2 = re.split(r"[\\]"+"['n']", StatePropLst1)
                        if StatePropLst2[1].find(':') != -1:
                            lst_index = 2
                        else:
                            lst_index = 1
                        StatePropLst3 = StatePropLst2[lst_index:]
                    else:
                        try:
                            StatePropLst2 = re.split(r"[\\]"+"['n']", DestProp)
                            if StatePropLst2[1].find(':') != -1:
                                lst_index = 1
                            else:
                                lst_index = 0
                            StatePropLst3 = StatePropLst2[lst_index:]
                        except:
                            StatePropLst3.append(DestProp)
                    # removes special characters in str
                    StatePropLst4 = []
                    for item in StatePropLst3:
                        item = re.split(r"[=]+|[\/]+|[*]+|[--]+|[++]+|[+]+|[-]+|[!]+|[,]+|[~]+|[%]+|[\^]+|[\|]+|[&]+|[\|\|]+|[&&]+|[']+|[>]+|[<]+|[>=]+|[<=]+|[==]+|[ ]+|[\[\]]+|[\(\)]", item)
                        StatePropLst4+=item
                    # removes the ';'
                    StatePropLst5 = []
                    StatePropLst6 = []
                    for j in range(0,len(StatePropLst4)):
                        if ';' in StatePropLst4[j]:
                            tp=StatePropLst4[j].partition(';')
                            StatePropLst5.append(list(tp[:-2])[0])
                        else:
                            StatePropLst5.append(StatePropLst4[j])

                    # removes space
                    le=len(StatePropLst4)
                    for i in range(0,le):
                        j=len(StatePropLst5[i].split())
                        if j != 0 :
                            StatePropLst6.append(StatePropLst5[i])
                    # removes keywords like if, else and elif
                    dataList = []
                    for item in StatePropLst6:
                        item = re.sub('if' , '', item)
                        item = re.sub('else', '', item)
                        item = re.sub('elif', '', item)
                        dataList.append(item)

                    StateDataLst = StateDataLst+dataList
                except:
                    pass
            for item in ChkItem:
                if str(item) in StateDataLst:
                    cnt = StateDataLst.count(str(item))
                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                         Rule_ID, 'The temporal logic \"'+str(item)+'" is used \"'+str(cnt)+'" times in the state machine')
                else:
                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                         Rule_ID, 'The temporal logic \"'+str(item)+'" is not used')

        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

    #-------------------------------------------------------------------------------------------
    def checkForActionsInFlowcharts_RCAPI(self, Rule_ID, ChkItem, ExceptionModule = []):
        if self.ModuleName not in ExceptionModule:
            srchKeysS1 = ['id','name']
            srchKeysS2 = ['chart','labelString']
            StateLst = []
            GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__SFlist, 'chart', srchKeysS1)
            GetStatsS2, PropDictS2, rSubLstS2, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__SFlist, 'state', srchKeysS2)
            # check to confirm flowchart
            for i in range(0,len(PropDictS1)):
                count = 0
                for j in range(0,len(PropDictS2)):
                    if( PropDictS2[j]['chart']==PropDictS1[i]['id']):
                        count=count+1
                        chartid = PropDictS1[i]['id']
                if count<2:
                    try:
                        for j in range(0,len(PropDictS2)):
                            if(PropDictS2[j]['chart']==chartid):
                                StateLst.append([PropDictS2[j]['labelString'], PropDictS1[i]['name']])
                    except:
                        pass
            for k in range(0,len(StateLst)):
                if StateLst[k][0].find(ChkItem) != -1:
                    cnt = StateLst[k][0].count(ChkItem)
                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                         Rule_ID, 'FlowChart: \"'+StateLst[k][1]+'" contains \"'+str(cnt)+'" number of State actions')
                else:
                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                         Rule_ID, 'There are no state actions present in Flow Chart')
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

    #-------------------------------------------------------------------------------------------
    def checkForSemiColonInActions_RCAPI(self, Rule_ID, ChkItem, ExceptionModule = []):
        if self.ModuleName not in ExceptionModule:
            srchKeysS1 = ['id','name']
            srchKeysS2 = ['labelString']
            StateLst = []
            GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__SFlist, 'chart', srchKeysS1)
            GetStatsS2, PropDictS2, rSubLstS2, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__SFlist, 'state', srchKeysS2)
            for Destitem in range(0,len(GetStatsS2)):
                try:
                    StateProp = PropDictS2[Destitem]['labelString']
                    StatePropLst3 = []
                    x = StateProp.find('/')
                    if x != -1:
                        StatePropLst = re.split(r"[\/]", StateProp)
                        StateName = StatePropLst[0]
                        StatePropLst1 = StatePropLst[1]
                        StatePropLst2 = re.split(r"[\\]"+"['n']", StatePropLst1)
                        StatePropLst3 = StatePropLst2
                    else:
                        try:
                            StatePropLst2 = re.split(r"[\\]"+"['n']", Destitem)
                            StatePropLst3 = StatePropLst2
                            StateName = 'untitled'
                        except:
                            StatePropLst3.append(Destitem)
                            StateName = 'untitled'
                    flag = 0
                    for item in StatePropLst3:
                        if '==' in item or '>=' in item or '<=' in item or '!=' in item or '~=' in item:
                            flag = 1
                        if flag == 0:
                            if '=' in item or '++' in item or '--' in item:
                                x=item.find(ChkItem)
                                if x == -1:
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName, Rule_ID,
                                         'Action in state \"'+StateName+'" does not terminate with semi colon')
                                else:
                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", " :: ", self.ModuleName, Rule_ID,
                                         'Action in state \"'+StateName+'" terminate with semi colon')
                except:
                    pass
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

    #-------------------------------------------------------------------------------------------

    def checkForOrderOfActions_RCAPI(self):
        Rule_ID = 'MISRA AC SLSF 055 A'
        srchKeysS1 = ['labelString']
        GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__SFlist, 'state', srchKeysS1)
        if (GetStatsS1>0):
            # collects the state info and forms a list of data items. Data is collected state by state.
            for i in range(0,len(PropDictS1)):
                StateDataLst = []
                try:
                    StatePropLst3 = []
                    x = PropDictS1[i].values()[0].find('/')
                    if x != -1:
                        StatePropLst = re.split(r"[\/]", PropDictS1[i].values()[0])
                        StateName = StatePropLst[0]
                        StatePropLst1 = StatePropLst[1]
                        StatePropLst2 = re.split(r"[\\]"+"['n']", StatePropLst1)
                        StatePropLst3 = StatePropLst2
                    else:
                        try:
                            StatePropLst2 = re.split(r"[\\]"+"['n']", PropDictS1[i]['labelString'])
                            StatePropLst3 = StatePropLst2
                            StateName = 'untitled'
                        except:
                            StatePropLst3.append(PropDictS1[i].values()[0])
                            StateName = 'untitled'
                    # removes space
                    le=len(StatePropLst3)
                    for i in range(0,le):
                        j=len(StatePropLst3[i].split())
                        if j != 0 :
                            StateDataLst.append(StatePropLst3[i])
                except:
                    pass
                # Collects the position of the action keywords found in data list and checks its order
                Actionlst = ['entry:','en:','during:','du:','exit:']
                pos_list = []
                end_result = True
                for item in Actionlst:
                    if item in StateDataLst:
                        pos_list.append(StateDataLst.index(item))
                        result = True
                        for posindex in range (0, (len(pos_list)-1)):
                            end_result = pos_list[posindex] < pos_list[posindex+1]
                            if end_result == False:
                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName, Rule_ID,
                                     '\"'+StateDataLst[pos_list[posindex+1]]+'" action is used before \"'+StateDataLst[pos_list[posindex]]+'" action in State \"'+StateName+'" ')
                            else:
                                self.dataLoggerObj.logCondResult("-", "-", "PASS", " :: ", self.ModuleName, Rule_ID,
                                     'The order of actions in state\"'+StateName+'" is correct')
                            end_result = result and end_result

    #-------------------------------------------------------------------------------------------

    def checkPropValueInLinkData_RCAPI(self, Rule_ID, InpList, CheckType, PropChkData, ExceptionModule = []):
        '''
        In each Line in the list, search the property.
        If property exists, check the value with the expected prop value. Otherwise,
        Check the expected property against the noted property.
        '''
        if self.ModuleName not in ExceptionModule:
            for propItem in PropChkData.keys():
                #process only if something is found in the list.
                for searchItem in range(0,len(InpList)):
                    lineName = '<unknown>'
                    lineType = '<unknown>'
                    lineType, lineName1 = self._getBlockInfo(InpList[searchItem])
                    if lineName1 != '<unknown>':
                        lineName = lineName1[0]
                    if propItem in InpList[searchItem].keys():
                        if CheckType == 'Exact':
                            # Compare the parsed parsed property value with the supplied value.
                            self.dataLoggerObj.logCompResult(PropChkData[propItem], InpList[searchItem][propItem], " :: ", 'POSTIVE', self.ModuleName,
                                  Rule_ID, 'Failure - The value of property \"'+propItem+'\" in Line \"'+lineName+'\" does not comply')
                        elif CheckType == 'Opposite':
                            # Compare the parsed parsed property value with the supplied value.
                            self.dataLoggerObj.logCompResult(PropChkData[propItem], InpList[searchItem][propItem], " :: ", 'NEGATIVE', self.ModuleName,
                                  Rule_ID, 'Failure - The value of property \"'+propItem+'\" in Line \"'+lineName+'\" does not comply')
                        elif CheckType == 'Any':
                            if InpList[searchItem][propItem] != '':
                                self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                     Rule_ID, 'The value of property \"'+propItem+'\" in Line \"'+lineName+'\" is not empty string')
                            else:
                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                     Rule_ID, 'The value of property \"'+propItem+'\" in Line \"'+lineName+'\" is empty string')
                    else:
                        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                             Rule_ID, 'Property \"'+propItem+'\" is not found in Line \"'+lineName+'\"')
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')
    #-------------------------------------------------------------------------------------------

    def checkPropValueInListType_RCAPI(self, Rule_ID, InpList, ListType, CheckType, PropChkData, ListFoundCheck = 'PASS', PropFoundCheck = 'FALSE', ExcludeBlock = [], ExceptionModule = []):
        '''
        In each block of the requested block type, search the property.
        If property exists, check the value with the expected prop value. Otherwise,
        Check the expected property against the noted property.
        '''
        if self.ModuleName not in ExceptionModule:
            for propItem in PropChkData.keys():
                srchKeys = []
                DefaultBlkData = {}
                srchKeys.append(propItem)
                srchKeys+=['BlockType', 'Name']
                GetStats, PropDict, rSubLst, CompltLst = self._getSrchDataFromBlck_RCAPI(InpList, ListType, srchKeys)
                #process only if something is found in the list.
                for searchItem in range(0,len(GetStats)):
                    if GetStats[searchItem] == 1:
                        blockName = '<unknown>'
                        blockType = '<unknown>'
                        blockType, blockName = self._getBlockInfo(PropDict[searchItem])
                        if propItem in PropDict[searchItem].keys():
                            if CheckType == 'Exact':
                                # Compare the parsed property value with the supplied value.
                                self.dataLoggerObj.logCompResult(PropChkData[propItem], PropDict[searchItem][propItem], " :: ", 'POSTIVE', self.ModuleName,
                                      Rule_ID, 'Failure - The value of property \"'+propItem+'\" in block \"'+blockName+'\" of type \"'+blockType+'\" in List \"'+ListType+'\" does not comply')
                            elif CheckType == 'Opposite':
                                # Compare the parsed property value with the supplied value.
                                self.dataLoggerObj.logCompResult(PropChkData[propItem], PropDict[searchItem][propItem], " :: ", 'NEGATIVE', self.ModuleName,
                                      Rule_ID, 'Failure - The value of property \"'+propItem+'\" in List \"'+ListType+'\" does not comply')
                            elif CheckType == 'Contains':
                                checkStr = str(PropDict[searchItem][propItem])
                                for checkItem in range(0,len(PropChkData[propItem])):
                                    if checkStr.find(PropChkData[propItem][checkItem]) != -1:
                                        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                             Rule_ID, 'The value of property \"'+propItem+'\" contains \"'+PropChkData[propItem][checkItem]+'\"')
                                    else:
                                        self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                             Rule_ID, 'The value of property \"'+propItem+'\" does not contain \"'+PropChkData[propItem][checkItem]+'\"')

                            # CheckType for Rule RP_0046. Checks for '~' and '~=' in label string
                            elif CheckType == 'DoesNotContain':
                                checkStr = str(PropDict[searchItem][propItem])
                                str_list = re.search(r'[~]+[=]|[~]', checkStr)
                                if str_list != None:
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                         Rule_ID, 'The value of property \"'+propItem+'\" in BlockType \"'+ListType+'" contains \"'+str_list.group()+'\" in \"'+checkStr+'\"')
                                else:
                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                         Rule_ID, 'The value of property \"'+propItem+'\" does not contain "~" or "~=" in \"'+checkStr+'\"')

                            elif CheckType =='Text':
                                if PropDict[searchItem].values()[0] == 'GROUP_STATE':

                                    LableName=list(self._getItemPosition(CompltLst[searchItem], 'labelString'))
                                    srchBlck = CompltLst[searchItem][LableName[0][0]]

                                    if srchBlck[1] != ' ' or '':
                                        stringOfGroup = srchBlck[1].split()
                                        for words in stringOfGroup:
                                            if  words.isalpha():
                                                self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                     Rule_ID, 'The value of property "lableString"  contain only text that is:\"'+srchBlck[1]+'\"')
                                            else:
		                                        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                     Rule_ID, 'The value of property "lableString" contain \"'+srchBlck[1]+'\",but this rule allows only text ')
                                        		break

                            elif CheckType == 'Otherthan':
                            # Checktype specifically designed for MISRA 48G
                                checkStr = str(PropDict[searchItem][propItem])
                                str_list = re.findall(r'[a-z\.]+[0-9\.]+|[[0-9\.]+|[^0-9\.]+]', checkStr)
                                for Item in str_list:
                                    try:
                                        val = eval(Item)
                                        if val in [0, 1]:
                                            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                 Rule_ID, 'The value of property \"'+propItem+'\" does not contains numerical literals other than "0" and "1"\"')
                                        else:
                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                 Rule_ID, 'The value of property \"'+propItem+'\" contains numerical literals \"'+str(Item)+'\"')
                                    except:
                                        pass

                            elif CheckType == 'Any':
                                if PropDict[searchItem][propItem] != '':
                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                         Rule_ID, 'The value of property \"'+propItem+'\" in block \"'+blockName+'\" of type \"'+blockType+'\" in List \"'+ListType+'\" is not empty string')
                                else:
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                         Rule_ID, 'The value of property \"'+propItem+'\" in block \"'+blockName+'\" of type \"'+blockType+'\" in List \"'+ListType+'\" is empty string')
                        else:
                            if PropFoundCheck == 'TRUE':
                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                     Rule_ID, 'Property \"'+propItem+'\" is not found in block \"'+blockName+'\" of type \"'+blockType+'\" in List \"'+ListType+'\"')
                            elif PropFoundCheck == 'FALSE':
                                self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                     Rule_ID, 'Property \"'+propItem+'\"found in block \"'+blockName+'\" of type \"'+blockType+'\" in List \"'+ListType+'\"')
                    else:
                        if ListFoundCheck == 'PASS':
                            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                 Rule_ID, 'Property \"'+propItem+'\"found in List \"'+ListType+'\"')
                        elif ListFoundCheck == 'FAIL':
                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                 Rule_ID, 'Property \"'+propItem+'\" is not found in List \"'+ListType+'\"')
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

    #-------------------------------------------------------------------------------------------
    def checkPropValue_RCAPI(self,Rule_ID,stateFlowInfo,srchKeysInChart,srchKeysInEvent,ExceptionModule = []):
        '''
	     Get the [id,name] values from all chart blocks in StateFlow.similerly get
         ['name','linkNode','scope','trigger'] from event block.now check the value of
         scope,if it is input or output event then trigger value should be funtion call
         type.
	    '''
        if self.ModuleName not in ExceptionModule:
            GetStats, PropDict, rSubLst, CompltLst = self._getSrchDataFromBlck_RCAPI(stateFlowInfo,'chart', srchKeysInChart)
            GetStats2, PropDict2, rSubLst2, CompltLst2 = self._getSrchDataFromBlck_RCAPI(stateFlowInfo,'event', srchKeysInEvent)
            for Indx in range(0,len(PropDict2)):
                if 'scope' in PropDict2[Indx].keys():
                    if PropDict2[Indx]['scope'] == 'INPUT_EVENT' or PropDict2[Indx]['scope'] == 'OUTPUT_EVENT':
                        name = '<unknown>'
                        for Indx2 in range(0,len(PropDict)):
                            if PropDict[Indx2]['id'] == int(PropDict2[Indx]['linkNode'][1]):
                                name = PropDict[Indx2]['name']+'/'+PropDict2[Indx]['name']
                        if PropDict2[Indx]['trigger'] == 'FUNCTION_CALL_EVENT':
                            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                 Rule_ID, 'The \"'+PropDict2[Indx]['scope']+' in \"'+name+'"is a function call event')
                        else:
                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                 Rule_ID, 'The \"'+PropDict2[Indx]['scope']+' in \"'+name+'" should be a function call event')

        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')



    #-------------------------------------------------------------------------------------------
    def checkcommentSFBlocks_RCAPI(self, Rule_ID, ChkItem, ExceptionModule = []):
        if self.ModuleName not in ExceptionModule:
            srchKeysS = ['labelString']
            GetStatsS, PropDictS, rSubLstS, CompltLst = self._getSrchDataFromBlck_RCAPI(self.__SFlist, 'state', srchKeysS)
            StatePropLst3 = []
            for i in range(0,len(PropDictS)):
                resultString = re.sub(re.compile("/\*.*?\*/",re.DOTALL ) ,"" ,PropDictS[i].values()[0])
                if len(resultString.split())>0:
                    if '/' in resultString:
                        StateAndAction = list(resultString.partition('/'))
                        if ChkItem in StateAndAction[2]:
                            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                 Rule_ID, 'The state \"'+StateAndAction[0]+'" is not empty')
                        else:
                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                 Rule_ID, 'The state \"'+StateAndAction[0]+'" has an empty action')
                    else:
                        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                             Rule_ID, 'The state has an empty action')
                else:
                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                         Rule_ID, 'The state has empty name and  empty action')

        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

	#--------------------------------------------------------------------------------------------

    def _getSrcDataByLink(self, SrcInput, DstInput, inpLst):
        # Get all the destination blocks property with search keys recorded.
        srchKeys = DstInput.keys()
        DestData  = self._getSrchDataFromSubBlck_RCAPI(inpLst['List'], 'Block', srchKeys)

        # Record all the source blocks property for the search keys.
        srchKeys = SrcInput.keys()
        SourceData  = self._getSrchDataFromSubBlck_RCAPI(inpLst['List'], 'Block', srchKeys)
        #Search the destination block and get the Match Key value.
        retLinkDataLst = []
        for DestDataItem in DestData:
            DestDataChck = len(DstInput.keys())
            DstLinkID = ''
            SrcLinkID = ''
            for DstInpKey in DstInput.keys():
                if DstInpKey in DestDataItem.keys():
                    if DstInput[DstInpKey] != '#MatchKey#':
                        if DstInput[DstInpKey] == DestDataItem[DstInpKey][0]:
                            DestDataChck -=1
                    else:
                        DstLinkID = DestDataItem[DstInpKey][0]
                        DestDataChck -=1
            # If match key value is found, then search the Link (Line) for destination block name
            # and get the soruce block name from the line.
            index = 0
            SrcLinkID = []
            if DestDataChck == 0:
                for LinkItem in inpLst['LinkData']:
                    if 'DstBlock' in LinkItem:
                        if DstLinkID in LinkItem['DstBlock']:
                            if 'SrcBlock' in LinkItem:
                                SrcLinkID.append(LinkItem['SrcBlock'][0])
                                index = index + 1
                # Search each source block having the name identified in the link block.
                # Collect the Values of the requested property.
                for srcIndex in range(0,index):
                    if SrcLinkID[srcIndex] != '':
                        for SrcDataItem in SourceData:
                            retDict = {}
                            SrcDataChck = 0
                            for SrcInpKey in SrcInput.keys():
                                if SrcInpKey in SrcDataItem.keys():
                                    retDict[SrcInpKey] = SrcDataItem[SrcInpKey]
                                    if SrcInput[SrcInpKey] == '#MatchKey#':
                                        if SrcLinkID[srcIndex] == SrcDataItem[SrcInpKey][0]:
                                            SrcDataChck = 1
                            #If the source value is found, search if there are any default property from the
                            # requested list.
                            if SrcDataChck == 1:
                                self._getDefaultProperty(retDict, SrcInput)
                                retLinkDataLst.append(retDict)
        return retLinkDataLst

    #-------------------------------------------------------------------------------------------
    def checkNoInputBusSignalForSFBlocks_RCAPI(self,Rule_ID,lineSrchKeys,blckSrckKeys,chartSrchKeys):
        '''
           Reteives the names of all charts and store them in chartInfo.Extract the output signal
		   name which have a output datatype BUS and store the signal names in busSignalsNames.
           Extract all Line information from .mdl file and store the result in LineInfo.If DstBlock
           value is in chartInfo then check the Name property value in same Line.If Name matches
           with any signal in busSignalsNames then raise Failure.
        '''
        busSignalsNames = []
        chartInfo = []
        SubSystemNames,PortDataOf1D,SubSystemPrpInfo,LineInfo,PortDataOf4D,PortDataOf8D,SystemInfo = self.SubSystemNamesUtil()
        inpLst, foundLst, Name = self._getNextList()
        while (foundLst == True):
            GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Block', blckSrckKeys)
            GetStatsS2, PropDictS2, rSubLstS2, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Line', lineSrchKeys)
            #retrieve chart names'
            PrptyPos=list(self._getItemPosition(inpLst['List'], chartSrchKeys[2]))
            if len(PrptyPos)>0:
                if inpLst['List'][PrptyPos[0][0]][1] == 'Stateflow':
                    PrptyPos=list(self._getItemPosition(inpLst['List'], chartSrchKeys[3]))
                    if len(PrptyPos) > 0:
                        if inpLst['List'][PrptyPos[0][0]][1] == 'Stateflow diagram':
                            Info = {}
                            PrptyPos=list(self._getItemPosition(inpLst['List'], chartSrchKeys[0]))
                            Info['Name']=inpLst['List'][PrptyPos[0][0]][1]

                            PrptyPos=list(self._getItemPosition(inpLst['List'], chartSrchKeys[1]))
                            Info['Ports']=inpLst['List'][PrptyPos[0][0]][1]
                            chartInfo.append(Info)
            #Retrive the Bus output datatype signal names of all Blocks.
            for srchPos in range(0,len(PropDictS1)):
                if 'OutDataTypeStr' in PropDictS1[srchPos].keys():
                    outputDataType = PropDictS1[srchPos]['OutDataTypeStr']
                    OutputDataSignal = outputDataType.split(':')
                    if OutputDataSignal[0] == 'Bus':
                        for srckKey in range(0,len(PropDictS2)):
                            if 'SrcBlock' in PropDictS2[srckKey].keys() and 'Name' in PropDictS2[srckKey].keys():
                                if PropDictS2[srckKey]['SrcBlock'] == PropDictS1[srchPos]['Name']:
                                    outputSignalName = PropDictS2[srckKey]['Name']
                                    if '<' in outputSignalName and '>' in outputSignalName:
                                        outputSignalName = outputSignalName[1:len(outputSignalName)-1]
                                    busSignalsNames.append(outputSignalName)
            inpLst, foundLst, Name = self._getNextList()
        #If Model have atleast one StateChart,then it start checking inputs
        for IndexerPos in range(0,len(chartInfo)):
            ports = chartInfo[IndexerPos]['Ports']
            if len(ports)>0:
                noOfChartInputs = 0
                if len(ports)==1 or len(ports)==2:
                    noOfChartInputs = chartInfo[IndexerPos]['Ports'][0]
                else:
                    if len(ports)==4:
                        noOfChartInputs = chartInfo[IndexerPos]['Ports'][0]+chartInfo[IndexerPos]['Ports'][3]
                if noOfChartInputs != 0:
                    for linePos in range(0,len(LineInfo)):
                        if 'DstBlock' in LineInfo[linePos].keys():
                            if LineInfo[linePos]['DstBlock'] == chartInfo[IndexerPos]['Name']:
                                if 'Name' in LineInfo[linePos].keys():
                                    signalName = LineInfo[linePos]['Name']
                                    if '<' in signalName and '>' in signalName:
                                        signalName = signalName[1:len(signalName)-1]
                                    if signalName in busSignalsNames:
                                        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                             Rule_ID,'Bus Signal \"'+signalName+'" should not be a input of State Chart for \"'+chartInfo[IndexerPos]['Name']+'".')
                                    else:
                                        self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                             Rule_ID,'Input Signal \"'+signalName+'" of State Chart \"'+chartInfo[IndexerPos]['Name']+'" is not a Bus signal')
    #-------------------------------------------------------------------------------------------
    def checkSignalLableAndPortNameShouldMatch_RCAPI(self,Rule_ID,blckSrckKeys,chartSrchKeys,ExceptionModule = []):
        '''
            Retrieve the inport and outport names of stateFlow, store them in InportList,
			OutportList respectively.Retrieve all line data into LineInfo.Now start
            comparing the LineInfo information with chart names.If DstBlock matched with
            any Cahrt name then compare its signal and port data based on its portnumber.
        '''
        InportList = []
        OutportList = []
        SubSystemNames,PortDataOf1D,SubSystemPrpInfo,LineInfo,PortDataOf4D,PortDataOf8D,SystemInfo = self.SubSystemNamesUtil()
        inpLst, foundLst, Name = self._getNextList()
        if self.ModuleName not in ExceptionModule:
            while (foundLst == True):
                InprtDict = {}
                outprtDict = {}
                GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Block', blckSrckKeys)
                #retrieve chart names'
                PrptyPos=list(self._getItemPosition(inpLst['List'], chartSrchKeys[2]))
                if len(PrptyPos)>0:
                    if inpLst['List'][PrptyPos[0][0]][1] == 'Stateflow':
                        PrptyPos=list(self._getItemPosition(inpLst['List'], chartSrchKeys[3]))
                        if len(PrptyPos) > 0:
                            if inpLst['List'][PrptyPos[0][0]][1] == 'Stateflow diagram':
       	                        PrptyPos=list(self._getItemPosition(inpLst['List'], chartSrchKeys[0]))
                                nameOfChart=inpLst['List'][PrptyPos[0][0]][1]
                                tInportList = []
                                tOutportList = []
                                for srckKey in range(0,len(PropDictS1)):
                                    tempList = []
                                    if PropDictS1[srckKey]['BlockType'] == 'Inport':
                                        portNumber='1'
                                        portName = 	PropDictS1[srckKey]['Name']
                                        if 'Port' in PropDictS1[srckKey].keys():
                                            portNumber = PropDictS1[srckKey]['Port']
                                        tempList.append(portNumber)
                                        tempList.append(portName)
                                        tInportList.append(tempList)

                                    if PropDictS1[srckKey]['BlockType'] == 'Outport':
                                        portNumber='1'
                                        portName = 	PropDictS1[srckKey]['Name']
                                        if 'Port' in PropDictS1[srckKey].keys():
                                            portNumber = PropDictS1[srckKey]['Port']
                                        tempList.append(portNumber)
                                        tempList.append(portName)
                                        tOutportList.append(tempList)
                                if len(tInportList)>0:
                                    InprtDict['Name'] = nameOfChart
                                    InprtDict['InprtInfo'] = tInportList
                                    InportList.append(InprtDict)
                                if len(tOutportList)>0:
                                    outprtDict['Name'] = nameOfChart
                                    outprtDict['OutportInfo'] = tOutportList
                                    OutportList.append(outprtDict)
                inpLst, foundLst, Name = self._getNextList()
            self.comparelableNameAndPortname(LineInfo,InportList,['DstBlock','DstPort','InprtInfo'],Rule_ID,self.ModuleName)
            self.comparelableNameAndPortname(LineInfo,OutportList,['SrcBlock','SrcPort','OutportInfo'],Rule_ID,self.ModuleName)
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

    #-------------------------------------------------------------------------------------------
    '''
       This function compares the signal lable name and destination block port name.
    '''
    def comparelableNameAndPortname(self,lineInfo,portInfo,srchKeys,Rule_ID,moduleName):
        for srchKey in range(0,len(lineInfo)):
            if srchKeys[0] in lineInfo[srchKey].keys() and 'Name' in lineInfo[srchKey].keys():
                for isrchKey in range(0,len(portInfo)):
                    if lineInfo[srchKey][srchKeys[0]] == portInfo[isrchKey]['Name']:
                        if srchKeys[1] in lineInfo[srchKey].keys():
                            blckPortInfo = portInfo[isrchKey][srchKeys[2]]
                            for srchPos in range(0,len(blckPortInfo)):
                                if str(lineInfo[srchKey][srchKeys[1]]) == blckPortInfo[srchPos][0]:
                                    signalName = lineInfo[srchKey]['Name']
                                    if '<' in signalName and '>' in signalName:
                                        signalName = signalName[1:len(signalName)-1]
                                    if signalName == blckPortInfo[srchPos][1]:
                                        self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", moduleName,
                                             Rule_ID,'In stateFlow \"'+portInfo[isrchKey]['Name']+'",portname \"'+blckPortInfo[srchPos][1]+'" and its signal name \"'+lineInfo[srchKey]['Name']+'" has matched.')
                                    else:
                                        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", moduleName,
                                             Rule_ID,'In stateFlow \"'+portInfo[isrchKey]['Name']+'",portname \"'+blckPortInfo[srchPos][1]+'" and its signal name \"'+lineInfo[srchKey]['Name']+'" has not matched.')

    #-------------------------------------------------------------------------------------------
    def checkEMLBlockdonotExist_RCAPI(self, Rule_ID,resultType,SFInfo,ExceptionModule = []):
        '''
		Misra 005: Retrieve all Embaded MATLAB Block Names from System properties and store it
		           in EMLNames.If EML Block exist,then immediately fail it. similerly if
				   ['Math','Trigonometry','InportShadow'] blocktypes are exist then fail.
        Misra 048: Retrieve ['id','name','type'] from chart block and check for isEML property
                   in all states.If it exist then notedown the ['chartId','lableString'].
                   If chart Id is exist in chratNames List,then fail this rule.
        Misra 039A:Retrieve ['id','lableString','chart','superState','treeNode'] from state.
                   check id of each state in treeNode first element in all states,if both are
                   matching then increment count.
        '''
        if self.ModuleName not in ExceptionModule:
            if resultType == 'NotExist':
                inpLst, foundLst, Name = self._getNextList()
                EMLNames = []
                funBlckResultType = 0
                inBlckResultType = 0
                while (foundLst == True):
                    #retrieve EML block names
                    PrptyPos=list(self._getItemPosition(inpLst['List'],'MaskType'))
                    if len(PrptyPos)>0:
                        if inpLst['List'][PrptyPos[0][0]][1] == 'Stateflow':
                            PrptyPos=list(self._getItemPosition(inpLst['List'],'MaskDescription'))
                            if len(PrptyPos) > 0:
                                if inpLst['List'][PrptyPos[0][0]][1] == 'Embedded MATLAB block':
       	                            PrptyPos=list(self._getItemPosition(inpLst['List'],'Name'))
                                    nameOfEMLBlck=inpLst['List'][PrptyPos[0][0]][1]
                                    nameOfEMLResult = 1
                                    EMLNames.append(nameOfEMLResult)
                                    if resultType == 'NotExist':
                                        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                             Rule_ID,'Embaded MATLAB Block: \"'+nameOfEMLBlck+'" is not a allowed Block in Simulink.')
                    GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Block', ['BlockType','Name'])
                    for srKey in range(0,len(PropDictS1)):
                        #checking for Function Block
                        if PropDictS1[srKey]['BlockType'] in ['Math','Trigonometry']:
                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                 Rule_ID,'Function Block:\"'+PropDictS1[srKey]['Name']+'" in \"'+Name+'" must not be used.')
                            funBlckResultType = 1
                            #checking for duplicate Inport
                        if PropDictS1[srKey]['BlockType'] == 'InportShadow':
                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                 Rule_ID,'Inport Block:\"'+PropDictS1[srKey]['Name']+'" in \"'+Name+'" is Duplicate Inport Block')
                            inBlckResultType = 1

                    inpLst, foundLst, Name = self._getNextList()
                if funBlckResultType == 0:
                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                         Rule_ID,'Function Block is not used in simulink.')
                if inBlckResultType == 0:
                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                         Rule_ID,'Duplicate Inport Blocks are not Exist')
                if len(EMLNames)==0:
                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                         Rule_ID,'Embaded MATLAB Block is not Exist')
            else:
                if resultType == 'Exist':
                    GetStats, PropDict, rSubLst, CompltLst = self._getSrchDataFromBlck_RCAPI(SFInfo,'chart',['id','name','type'])
                    PrptyPos=list(self._getItemPosition(SFInfo,'state'))
                    if Rule_ID == 'MISRA AC SLSF 048 B':
                        EMLInfo = []
                        for srchKey in range(0,len(PrptyPos)):
                            stateDict = {}
                            stateInfo = SFInfo[PrptyPos[srchKey][0]]
                            GetStats2, PropDict2, rSubLst2, CompltLst2 = self._getSrchDataFromBlck_RCAPI(stateInfo,'eml',['isEML'])
                            if len(PropDict2)>0:
                                PrptyPos2=list(self._getItemPosition(stateInfo,'chart'))
                                if len(PrptyPos2)>0:
                                    stateDict['chartID']=stateInfo[PrptyPos2[0][0]][1]
                                    PrptyPos3=list(self._getItemPosition(stateInfo,'labelString'))
                                    if len(PrptyPos3)>0:
                                        stateDict['lableString']=stateInfo[PrptyPos3[0][0]][1]
                                        EMLInfo.append(stateDict)
                        chratNames = []
                        for srchPos in range(0,len(PropDict)):
                            if len(PropDict[srchPos]) == 2:
                                chratNames.append(PropDict[srchPos])
                        for chartIndex in range(0,len(chratNames)):
                            resultFound = 0
                            for EMLIndex in range(0,len(EMLInfo)):
                                if chratNames[chartIndex]['id'] == EMLInfo[EMLIndex]['chartID']:
                                    resultFound = 1
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                         Rule_ID,'Embaded Matlab Block:\"'+EMLInfo[EMLIndex]['lableString']+'" is not allowed in stateFlow :\"'+chratNames[chartIndex]['name']+'"')
                            if resultFound == 0:
                                self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                     Rule_ID,'Embaded Matlab Block is not Exist in stateFlow :\"'+chratNames[chartIndex]['name']+'"')
                    else:
                        if Rule_ID == 'MISRA AC SLSF 039 A':
                            stateInfoList = []
                            #Retrieve ['id','name','lableString','superState'] properties from all states
                            for srchKey in range(0,len(PrptyPos)):
                                stateDict = {}
                                stateInfo = SFInfo[PrptyPos[srchKey][0]]
                                PrptyPos2=list(self._getItemPosition(stateInfo,'chart'))
                                if len(PrptyPos2)>0:
                                    stateDict['chartID']=stateInfo[PrptyPos2[0][0]][1]
                                PrptyPos2=list(self._getItemPosition(stateInfo,'labelString'))
                                if len(PrptyPos2)>0:
                                    stateDict['lableString']=stateInfo[PrptyPos2[0][0]][1]
                                else:
                                    stateDict['lableString']='<unknown>'
                                PrptyPos2=list(self._getItemPosition(stateInfo,'id'))
                                if len(PrptyPos2)>0:
                                    stateDict['id']=stateInfo[PrptyPos2[0][0]][1]
                                PrptyPos2=list(self._getItemPosition(stateInfo,'superState'))
                                if len(PrptyPos2)>0:
                                    stateDict['superState']=stateInfo[PrptyPos2[0][0]][1]
                                PrptyPos2=list(self._getItemPosition(stateInfo,'treeNode'))
                                if len(PrptyPos2)>0:
                                    stateDict['treeNode']=stateInfo[PrptyPos2[0][0]][1]
                                stateInfoList.append(stateDict)
                            for indexOfState in range(0,len(stateInfoList)):
                                noOfSubStates = 0
                                if 'superState' in stateInfoList[indexOfState].keys():
                                    if stateInfoList[indexOfState]['superState'] == 'GROUPED':
                                        for IndexOfSubState in range(0,len(stateInfoList)):
                                            if 'treeNode' in stateInfoList[IndexOfSubState].keys():
                                                treeNodeValue=stateInfoList[IndexOfSubState]['treeNode']
                                                treeNodeValue=treeNodeValue.split()
                                                intiNodeValue = treeNodeValue[0][1:]
                                                if str(stateInfoList[indexOfState]['id']) == str(intiNodeValue):
                                                    noOfSubStates = noOfSubStates+1
                                        if noOfSubStates == 0:
                                            for chartKey in range(0,len(PropDict)):
                                                if str(PropDict[chartKey]['id']) == str(stateInfoList[indexOfState]['chartID']):
                                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                         Rule_ID,'State:\"'+stateInfoList[indexOfState]['lableString']+'" has zero subStates in Chart:"'+PropDict[chartKey]['name']+'"')

                                        else:
                                            if noOfSubStates>1:
                                                self.mutualState.append(stateInfoList[indexOfState])
                                                for chartKey in range(0,len(PropDict)):
                                                    if str(PropDict[chartKey]['id']) == str(stateInfoList[indexOfState]['chartID']):
                                                        self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                             Rule_ID,'State:\"'+stateInfoList[indexOfState]['lableString']+'" has more than one subStates in Chart:"'+PropDict[chartKey]['name']+'"')
                                            else:
                                                if noOfSubStates == 1:
                                                    for chartKey in range(0,len(PropDict)):
                                                        if str(PropDict[chartKey]['id']) == str(stateInfoList[indexOfState]['chartID']):
                                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                 Rule_ID,'State:\"'+stateInfoList[indexOfState]['lableString']+'" has Only one subStates in Chart:"'+PropDict[chartKey]['name']+'"')
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

    #-------------------------------------------------------------------------------------------
    def checkconditionalAndTransitionalAction_RCAPI(self,Rule_ID,stateFlowInfo,srchKeys,ExceptionModule = []):
        '''
            this rule will fail the conditional and transitional actions, when it appears in the
			form of:%[]{}/%
            so First search position(pos1) of ] and check for string[pos1+1]=={,
            similerly for / after }.In this case this rule will fail.
        '''
        if self.ModuleName not in ExceptionModule:
            #find all chart names and [lableString,Name]
            GetStatsS1, PropDictS1, rSubLstS1, CompltLst = self._getSrchDataFromBlck_RCAPI(stateFlowInfo,'chart',['name','id'])
            GetStatsS2, PropDictS2, rSubLstS2, CompltLst2 = self._getSrchDataFromBlck_RCAPI(stateFlowInfo,'transition',srchKeys)
            resultStatus = False
            for srchKey in range(0,len(PropDictS2)):
                if 	'labelString' in PropDictS2[srchKey].keys():
                    lableString = PropDictS2[srchKey]['labelString']
                    #fetch the initial position of [,]
                    noCount = lableString.count('[')
                    ncCount = lableString.count(']')
                    if ncCount > 0 and noCount>0:
                        if noCount == ncCount:
                            OMatch = lableString.find('[')
                            CMatch = lableString.find(']')
                            if CMatch > OMatch:
                                noFCount = lableString.count('{')
                                ncFCount = lableString.count('}')
                                if ncFCount > 0 and noFCount > 0:
                                    Match2 = lableString.find('}')
                                    if ncFCount == noFCount:
                                        if lableString[CMatch+1] == '{':
                                            actionStringPos = lableString.find('/')
                                            if actionStringPos > -1:
                                                if lableString[Match2+1]=='/':
                                                    for chartKey in range(0,len(PropDictS1)):
                                                        if PropDictS2[srchKey]['chart'] == PropDictS1[chartKey]['id']:
                                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                 Rule_ID, 'condition-action and transition-action:\"'+PropDictS2[srchKey]['labelString']+'" must not be used in same machine in chart:\"'+PropDictS1[chartKey]['name']+'"')
                                                    resultStatus = True
            if resultStatus	== False:
                for chartKey in range(0,len(PropDictS1)):
                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                         Rule_ID, 'condition-action and transition-action not used in same machine in chart:\"'+PropDictS1[chartKey]['name']+'"')
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

    #-------------------------------------------------------------------------------------------
    def checkTransitionProperties_RCAPI(self,Rule_ID,stateFlowInfo,MatchType,ExceptionModule = []):
        '''
            Note:    To differentiating the default transition and general transition
                     we need to count the number of properties in src block which is in
					 tansition Block.if the count is one that means default transition
                     otherwise general transition.
           Misra 42A:
		             extract the [id,linkNode,chart,lableString]:value1 properties and store them in 
                     defaultTrans if src count is one otherwise TransitionInfo.
                     self.mutualState:value2 contains the exclusive state information.
                     compare value1[id] with value2[linkNode[0]].if match, then increment count 
                     if count is one then this rule will pass else raise failure. 					 
			
        '''
        if self.ModuleName not in ExceptionModule:

            GetStats, PropDict, rSubLst, CompltLst = self._getSrchDataFromBlck_RCAPI(stateFlowInfo,'chart',['id','name'])
            transitionPos=list(self._getItemPosition(stateFlowInfo,'transition'))
            transitionList = []
            defaultTrans = []
            TransitionInfo = []

            for transPos in range(0,len(transitionPos)):
                if len(transitionPos[transPos])==2:
                    if transitionPos[transPos][1] == 0:
                        transitionList.append(transitionPos[transPos][0])
            for IndexKey in range(0,len(transitionList)):
                transitionData = stateFlowInfo[transitionList[IndexKey]]
                transitionPos=list(self._getItemPosition(transitionData,'src'))
                transitionPos2=list(self._getItemPosition(transitionData,'dst'))
                if len(transitionPos[0])==2:
                    if transitionPos[0][1] == 0:
                        #note down the Default Transition values
                        dataValues = {}
                        #id value
                        idPos=list(self._getItemPosition(transitionData,'id'))
                        for idIndex in range(0,len(idPos)):
                            if len(idPos[idIndex]) == 2:
                                if idPos[idIndex][1] == 0:
                                    dataValues['id'] = transitionData[idPos[idIndex][0]][1]
                        #labelString value
                        lablePos=list(self._getItemPosition(transitionData,'labelString'))
                        for idIndex in range(0,len(lablePos)):
                            if len(lablePos[idIndex]) == 2:
                                if lablePos[idIndex][1] == 0:
                                    dataValues['lableString'] = transitionData[lablePos[idIndex][0]][1]
                        #chart id value
                        chartPos=list(self._getItemPosition(transitionData,'chart'))
                        for idIndex in range(0,len(chartPos)):
                            if len(chartPos[idIndex]) == 2:
                                if chartPos[idIndex][1] == 0:
                                    dataValues['cahrtid'] = transitionData[chartPos[idIndex][0]][1]
                        #Linknode value
                   	    linkPos=list(self._getItemPosition(transitionData,'linkNode'))
                        for idIndex in range(0,len(linkPos)):
                            if len(linkPos[idIndex]) == 2:
                                if linkPos[idIndex][1] == 0:
                                    dataValues['linkInfo'] = transitionData[linkPos[idIndex][0]][1]
                        #print dataValues
                        if len(transitionData[transitionPos[0][0]]) == 2:
                            defaultTrans.append(dataValues)
                        else:
                            srcIntrsc = transitionData[transitionPos[0][0]][2][1]
                            dstIntrsc = transitionData[transitionPos2[0][0]][2][1]
                            srcid = transitionData[transitionPos[0][0]][1][1]
                            dstid = transitionData[transitionPos2[0][0]][1][1]
                            dataValues['srcid'] = srcid							
                            dataValues['dstid'] = dstid							
                            dataValues['src'] = srcIntrsc							
                            dataValues['dst'] = dstIntrsc							
                            TransitionInfo.append(dataValues)
            if MatchType == 'Exist':
                if len(self.mutualState) == 0:
                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                        Rule_ID, 'Exclusive states are not exist in chart')
                else:
                    if len(defaultTrans) == 0:
                        for sIndexer in range(0,len(self.mutualState)):
                            for cIndexer in range(0,len(PropDict)):
                                if PropDict[cIndexer]['id'] == self.mutualState[sIndexer]['chartID']:
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                         Rule_ID, 'A super-state:\"'+self.mutualState[sIndexer]['lableString']+'" in Chart:\"'+PropDict[cIndexer]['name']+'" containing exclusive states,so it should have one default transition ')
                    else:
                        for sIndexer in range(0,len(self.mutualState)):
                            noOfDefaultTrans = 0
                            for tIndexer in range(0,len(defaultTrans)):
                                if 'linkInfo' in defaultTrans[tIndexer].keys():
                                    treeNodeValue=defaultTrans[tIndexer]['linkInfo']
                                    treeNodeValue=treeNodeValue.split()
                                    intiNodeValue=treeNodeValue[0][1:]

                                    if str(self.mutualState[sIndexer]['id']) == str(intiNodeValue):
                                        noOfDefaultTrans = noOfDefaultTrans+1
                            if noOfDefaultTrans == 1:
                                for cIndexer in range(0,len(PropDict)):
                                    if PropDict[cIndexer]['id'] == self.mutualState[sIndexer]['chartID']:
                                        self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                             Rule_ID, 'A super-state:\"'+self.mutualState[sIndexer]['lableString']+'" in Chart:\"'+PropDict[cIndexer]['name']+'" contains exclusive states and it has only one default transition ')
                            else:
                                if noOfDefaultTrans > 1: 							
                                    for cIndexer in range(0,len(PropDict)):
                                        if PropDict[cIndexer]['id'] == self.mutualState[sIndexer]['chartID']:
                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                 Rule_ID, 'A super-state:\"'+self.mutualState[sIndexer]['lableString']+'" containing exclusive states must have only one default transition in Chart:\"'+PropDict[cIndexer]['name']+'"')
                                else:
                                    if noOfDefaultTrans == 0: 							
                                        for cIndexer in range(0,len(PropDict)):
                                            if PropDict[cIndexer]['id'] == self.mutualState[sIndexer]['chartID']:
                                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                     Rule_ID, 'A super-state:\"'+self.mutualState[sIndexer]['lableString']+'" containing exclusive states must have one default transition in Chart:\"'+PropDict[cIndexer]['name']+'"')
            else:
                if MatchType=='Single':
                    GetStats2, PropDict2, rSubLst2, CompltLst2 = self._getSrchDataFromBlck_RCAPI(stateFlowInfo,'state',['id','chart','labelString'])
                    if len(PropDict2) == 0:
                        for cIndexer in range(0,len(PropDict)): 					
                            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                 Rule_ID, 'States are not exist in chart:\"'+PropDict[cIndexer]['name']+'"')					     
                    else:								 
                        for SsrchIndx in range(0,len(PropDict2)):
                            noOfDefaultStates = 0					
                            for TsrchIndx in range(0,len(defaultTrans)):
                                if 'linkInfo' in defaultTrans[TsrchIndx].keys():
                                    treeNodeValue=defaultTrans[TsrchIndx]['linkInfo']
                                    treeNodeValue=treeNodeValue.split()
                                    intiNodeValue=treeNodeValue[0][1:]
                                    if str(PropDict2[SsrchIndx]['id'])==str(intiNodeValue):
                                        noOfDefaultStates = noOfDefaultStates+1
                            if noOfDefaultStates == 1:
                                for cIndexer in range(0,len(PropDict)):
                                    if PropDict[cIndexer]['id'] == PropDict2[SsrchIndx]['chart']:
                                        if 'labelString' in PropDict2[SsrchIndx].keys():									
                                            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                 Rule_ID, 'State:\"'+PropDict2[SsrchIndx]['labelString']+'" has only one default transition in Chart:\"'+PropDict[cIndexer]['name']+'"')
                                        # else:
                                            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                 Rule_ID, 'State:<unknown> has only one default transition in Chart:\"'+PropDict[cIndexer]['name']+'"')
                            else:
                                if noOfDefaultStates > 1: 							
                                    for cIndexer in range(0,len(PropDict)):
                                        if PropDict[cIndexer]['id'] == PropDict2[SsrchIndx]['chart']:
                                            if 'labelString' in PropDict2[SsrchIndx].keys():									
                                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                     Rule_ID, 'State:\"'+PropDict2[SsrchIndx]['labelString']+'" Must contain no more than one default transition in Chart:\"'+PropDict[cIndexer]['name']+'"')
                                            else:
                                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                     Rule_ID, 'State:<unknown> Must contain no more than one default transition in Chart::\"'+PropDict[cIndexer]['name']+'"')                                            										
                                else:
                                    if noOfDefaultStates == 0: 							
                                        for cIndexer in range(0,len(PropDict)):
                                            if PropDict[cIndexer]['id'] == PropDict2[SsrchIndx]['chart']:
                                                if 'labelString' in PropDict2[SsrchIndx].keys():									
                                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                         Rule_ID, 'State:\"'+PropDict2[SsrchIndx]['labelString']+'" should contain one default transition in Chart:\"'+PropDict[cIndexer]['name']+'"')
                                                else:
                                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                         Rule_ID, 'State:<unknown> should contain one default transition in Chart::\"'+PropDict[cIndexer]['name']+'"')                                            										
                else:
                    if MatchType=='DefaultAtTop':
                        for csrchIndx in range(0,len(PropDict)):
                            noOfDefaultStates = 0					
                            for TsrchIndx in range(0,len(defaultTrans)):
                                if 'linkInfo' in defaultTrans[TsrchIndx].keys():
                                    treeNodeValue=defaultTrans[TsrchIndx]['linkInfo']
                                    treeNodeValue=treeNodeValue.split()
                                    intiNodeValue=treeNodeValue[0][1:]
                                    if str(PropDict[csrchIndx]['id'])==str(intiNodeValue):
                                        noOfDefaultStates = noOfDefaultStates+1
                            if noOfDefaultStates == 1:
                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                         Rule_ID, 'Top level of the state machine contain only one default transition in Chart:\"'+PropDict[csrchIndx]['name']+'"')
                            else:
                                if noOfDefaultStates > 1: 							
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                         Rule_ID, 'Top level of the state machine Must contain only one default transition in Chart:\"'+PropDict[csrchIndx]['name']+'"')
                                else:
                                    if noOfDefaultStates == 0: 							
                                        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                             Rule_ID, 'Top level of the state machine Must contain one default transition in Chart:\"'+PropDict[csrchIndx]['name']+'"')
                    else:
                        if MatchType=='NotExist':
                            isThatExist = False
                            duplicateList = TransitionInfo							
                            for srcIndex in range(0,len(TransitionInfo)):
                                srcintrsctPnts = TransitionInfo[srcIndex]['src']
                                srcintrsctPntsLst = srcintrsctPnts.split()
                                srcList = srcintrsctPntsLst[4:6]
                                interList1 = srcList[0]
                                interList2 = srcList[1]
                       	        interList1 = interList1.split('.')[0]							
                       	        interList2 = interList2.split('.')[0]
                                for dstIndex in range(0,len(TransitionInfo)):
                                    dstintrsctPnts = TransitionInfo[dstIndex]['dst']
                                    dstintrsctPntsLst = dstintrsctPnts.split()
                                    dstList = dstintrsctPntsLst[4:6]
                                    interList3 = dstList[0]
                                    interList4 = dstList[1]
                                    interList3 = interList3.split('.')[0]							
                                    interList4 = interList4.split('.')[0]
                                    if str(interList1) == str(interList3) and str(interList2) == str(interList4):
                                        isThatExist = True				
                                        if 'lableString' in TransitionInfo[srcIndex].keys() and 'lableString' in TransitionInfo[dstIndex].keys():									
                                            for indxKey in range(0,len(PropDict)):										
                                                if PropDict[indxKey]['id'] == TransitionInfo[dstIndex]['cahrtid']:   											
                                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                         Rule_ID, 'transitions:\"'+TransitionInfo[dstIndex]['lableString']+'" and \"'+TransitionInfo[srcIndex]['lableString']+'" must not be drawn one upon the other in chart:\"'+PropDict[indxKey]['name']+'"')									
                                        else:
                                            for indxKey in range(0,len(PropDict)):										
                                                if PropDict[indxKey]['id'] == TransitionInfo[dstIndex]['cahrtid']:   											
                                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                         Rule_ID, 'transitions:<unknown> and <unknown> must not be drawn one upon the other in chart:\"'+PropDict[indxKey]['name']+'"')									
                            if isThatExist == False:
                                for indxKey in range(0,len(PropDict)):										
                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                         Rule_ID, 'transitions were not drawn one upon the other in chart:\"'+PropDict[indxKey]['name']+'"')							
                        else:
                            if MatchType=='Unguarded_Exist':
                                JGetStats, JPropDict, JrSubLst, JCompltLst = self._getSrchDataFromBlck_RCAPI(stateFlowInfo,'junction',['id','chart','linkNode'])								
                                SGetStats, SPropDict, SrSubLst, SCompltLst = self._getSrchDataFromBlck_RCAPI(stateFlowInfo,'state',['id','labelString','type'])								
                                for JIndex in range(0,len(JPropDict)):
                                    condTr = 0
                                    uncondTr = 0
                                    for TrIndex in range(0,len(TransitionInfo)):
                                        if JPropDict[JIndex]['id'] == TransitionInfo[TrIndex]['srcid']:
                                            if 'lableString' in TransitionInfo[TrIndex].keys():
                                                condTr = condTr+1
                                            else:
                                                uncondTr = uncondTr+1	
                                    if uncondTr == 1:
                                        linkNodeValue=JPropDict[JIndex]['linkNode']
                                        linkNodeValue=linkNodeValue.split()
                                        intiNodeValue=str(linkNodeValue[0][1:])
                                        junctionExist = False		
                                        #if the junction exist in flow chart or graphical function										
                                        for SIndex in range(0,len(SPropDict)):
                                            if str(SPropDict[SIndex]['id']) == intiNodeValue:
                                                junctionExist = True											
                                                for CIndex in range(0,len(PropDict)):
                                                    if PropDict[CIndex]['id'] == JPropDict[JIndex]['chart']:											
                                                        if SPropDict[SIndex]['type'] == 'FUNC_STATE':	
                                                            if Rule_ID == 'MISRA AC SLSF 043 I':														
                                                                if 'labelString' in SPropDict[SIndex].keys():												
                                                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                                        Rule_ID,'Junction in graphical function:\"'+SPropDict[SIndex]['labelString']+'" has exactly one default path in chart:\"'+PropDict[CIndex]['name']+'".')
                                                                else:
                                                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                                        Rule_ID,'Junction in graphical function:<unKnown> has exactly one default path in chart:\"'+PropDict[CIndex]['name']+'".')
                                                            else:
                                                                if 'labelString' in SPropDict[SIndex].keys():												
                                                                    self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,
                                                                        Rule_ID,'MANUAL CHECK RULE:Default path from Junction in graphical function:\"'+SPropDict[SIndex]['labelString']+'" Must have unguarded path to state in chart:\"'+PropDict[CIndex]['name']+'".')
                                                                else:
                                                                    self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,
                                                                        Rule_ID,'MANUAL CHECK RULE:Default path from Junction in graphical function:<unknown> Must have unguarded path to state in chart:\"'+PropDict[CIndex]['name']+'".')
                                                                															
                                                        else:
                                                            if Rule_ID == 'MISRA AC SLSF 043 I':														
                                                                if 'labelString' in SPropDict[SIndex].keys():												
                                                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                                         Rule_ID,'Junction in state:\"'+SPropDict[SIndex]['labelString']+'" has exactly one default path in chart:\"'+PropDict[CIndex]['name']+'".')
                                                                else:
                                                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                                         Rule_ID,'Junction in state:<unKnown> has exactly one default path in chart:\"'+PropDict[CIndex]['name']+'".')
                                                            else:
                                                                if 'labelString' in SPropDict[SIndex].keys():												
                                                                    self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,
                                                                        Rule_ID,'MANUAL CHECK RULE:Default path from Junction in graphical function:\"'+SPropDict[SIndex]['labelString']+'" Must have unguarded path to state in chart:\"'+PropDict[CIndex]['name']+'".')
                                                                else:
                                                                    self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,
                                                                        Rule_ID,'MANUAL CHECK RULE:Default path from Junction in graphical function:<unknown> Must have unguarded path to state in chart:\"'+PropDict[CIndex]['name']+'".')
															
                                        #if the juntion exist at chart root level itself																 
                                        if junctionExist == False:
                                            for CIndex in range(0,len(PropDict)):
                                                if str(PropDict[CIndex]['id']) == intiNodeValue:
                                                    if Rule_ID == 'MISRA AC SLSF 043 I':												
                                                        self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                             Rule_ID,'junction has exactly one default path in chart:\"'+PropDict[CIndex]['name']+'".')										
                                                    else:
                                                        self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,
                                                            Rule_ID,'MANUAL CHECK RULE:Default path from Junction Must have unguarded path to state in chart:\"'+PropDict[CIndex]['name']+'".')
													
                                    else:
                                        if Rule_ID == 'MISRA AC SLSF 043 I':									
                                            if uncondTr > 1:
                                                linkNodeValue=JPropDict[JIndex]['linkNode']
                                                linkNodeValue=linkNodeValue.split()
                                                intiNodeValue=str(linkNodeValue[0][1:])
                                                junctionExist = False		
                                                #if the junction exist in flow chart or graphical function										
                                                for SIndex in range(0,len(SPropDict)):
                                                    if str(SPropDict[SIndex]['id']) == intiNodeValue:
                                                        junctionExist = True											
                                                        for CIndex in range(0,len(PropDict)):
                                                            if PropDict[CIndex]['id'] == JPropDict[JIndex]['chart']:											
                                                                if SPropDict[SIndex]['type'] == 'FUNC_STATE':									
                                                                    if 'labelString' in SPropDict[SIndex].keys():												
                                                                        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                            Rule_ID,'Junction in graphical function:\"'+SPropDict[SIndex]['labelString']+'" has more than one default path in chart:\"'+PropDict[CIndex]['name']+'".')
                                                                    else:
                                                                        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                            Rule_ID,'Junction in graphical function:<unKnown> has more than one default path in chart:\"'+PropDict[CIndex]['name']+'".')
                                                                else:
                                                                    if 'labelString' in SPropDict[SIndex].keys():												
                                                                        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                            Rule_ID,'Junction in state:\"'+SPropDict[SIndex]['labelString']+'" has more than one default path in chart:\"'+PropDict[CIndex]['name']+'".')
                                                                    else:
                                                                        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                            Rule_ID,'Junction in state:<unKnown> has more than one default path in chart:\"'+PropDict[CIndex]['name']+'".')
                                            #if the juntion exist at chart root level itself																 
                                                if junctionExist == False:
                                                    for CIndex in range(0,len(PropDict)):
                                                        if str(PropDict[CIndex]['id']) == intiNodeValue: 											
                                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                 Rule_ID,'junction has more than one default path in chart:\"'+PropDict[CIndex]['name']+'".')										
                                            else:
                                                if condTr>0 and uncondTr==0:
                                                    linkNodeValue=JPropDict[JIndex]['linkNode']
                                                    linkNodeValue=linkNodeValue.split()
                                                    intiNodeValue=str(linkNodeValue[0][1:])
                                                    junctionExist = False		
                                                    #if the junction exist in flow chart or graphical function										
                                                    for SIndex in range(0,len(SPropDict)):
                                                        if str(SPropDict[SIndex]['id']) == intiNodeValue:
                                                            junctionExist = True											
                                                            for CIndex in range(0,len(PropDict)):
                                                                if PropDict[CIndex]['id'] == JPropDict[JIndex]['chart']:											
                                                                    if SPropDict[SIndex]['type'] == 'FUNC_STATE':									
                                                                        if 'labelString' in SPropDict[SIndex].keys():												
                                                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                                Rule_ID,'Junction in graphical function:\"'+SPropDict[SIndex]['labelString']+'" has no default path in chart:\"'+PropDict[CIndex]['name']+'".')
                                                                        else:
                                                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                                Rule_ID,'Junction in graphical function:<unKnown> has no default path in chart:\"'+PropDict[CIndex]['name']+'".')
                                                                    else:
                                                                        if 'labelString' in SPropDict[SIndex].keys():												
                                                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                                Rule_ID,'Junction in state:\"'+SPropDict[SIndex]['labelString']+'" has no default path in chart:\"'+PropDict[CIndex]['name']+'".')
                                                                        else:
                                                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                                Rule_ID,'Junction in state:<unKnown> has no default path in chart:\"'+PropDict[CIndex]['name']+'".')
                                                    #if the juntion exist at chart root level itself																 
                                                    if junctionExist == False:
                                                        for CIndex in range(0,len(PropDict)):
                                                            if str(PropDict[CIndex]['id']) == intiNodeValue: 											
                                                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                                     Rule_ID,'junction has no default path in chart:\"'+PropDict[CIndex]['name']+'".')										
                            else:
                                if MatchType=='DefaultTx_Exist':
                                        SGetStats, SPropDict, SrSubLst, SCompltLst = self._getSrchDataFromBlck_RCAPI(stateFlowInfo,'state',['id','labelString','type'])								
                                        #if the junction exist in flow chart or graphical function										
                                        for DTIndex in range(0,len(defaultTrans)):
                                            junctionExist=False										
                                            linkNodeValue=defaultTrans[DTIndex]['linkInfo']
                                            linkNodeValue=linkNodeValue.split()
                                            intiNodeValue=str(linkNodeValue[0][1:]) 										
                                            for SIndex in range(0,len(SPropDict)):
                                                if str(SPropDict[SIndex]['id']) == intiNodeValue:
                                                    junctionExist = True											
                                                    for CIndex in range(0,len(PropDict)):
                                                        if PropDict[CIndex]['id'] == defaultTrans[DTIndex]['cahrtid']:											
                                                            if SPropDict[SIndex]['type'] == 'FUNC_STATE':	
                                                                if 'labelString' in SPropDict[SIndex].keys():												
                                                                    self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,
                                                                         Rule_ID,'MANUAL CHECK RULE:Default transition in graphical function:\"'+SPropDict[SIndex]['labelString']+'" Must not cross the state boundaries in chart:\"'+PropDict[CIndex]['name']+'".')
                                                                else:
                                                                    self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,
                                                                         Rule_ID,'MANUAL CHECK RULE:Default transition in graphical function:<unknown> Must not cross the state boundaries in chart:\"'+PropDict[CIndex]['name']+'".')
                                                                															
                                                            else:
                                                                if 'labelString' in SPropDict[SIndex].keys():												
                                                                    self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,
                                                                        Rule_ID,'MANUAL CHECK RULE:Default transition in state:\"'+SPropDict[SIndex]['labelString']+'" Must not cross the state boundaries in chart:\"'+PropDict[CIndex]['name']+'".')
                                                                else:
                                                                    self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,
                                                                        Rule_ID,'MANUAL CHECK RULE:Default transition in state:<unknown> Must not cross the state boundaries in chart:\"'+PropDict[CIndex]['name']+'".')
                                            if junctionExist == False:
                                                for CIndex in range(0,len(PropDict)):
                                                    if str(PropDict[CIndex]['id']) == intiNodeValue: 											
                                                        self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,
                                                             Rule_ID,'MANUAL CHECK RULE:Default transition in chart:\"'+PropDict[CIndex]['name']+'"  Must not cross the state boundaries.')										
  																		
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

    #--------------------------------------------------------------------------------------------
    def checkSrcDataByLink_RCAPI(self, Rule_ID, SrcInput, DstInput, CheckList):
        inpLst, foundLst, Name = self._getNextList()
        while (foundLst == True):
            if len(inpLst) > 0:
                LinkData = self._getSrcDataByLink(SrcInput, DstInput, inpLst)
                for LinkDataitem in LinkData:
                    if 'Name' in LinkDataitem:
                        BlockName = LinkDataitem['Name'][0]
                    else:
                        BlockName = '<unknown>'

                    if CheckList['CheckExp'] == 'MANUAL':
                        self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,
                             Rule_ID, 'Please manually check whether the properties of block \"'+BlockName+'\" complies with the rule')
                    elif CheckList['CheckItem'] in LinkDataitem:
                        proceed = True
                        if len(LinkDataitem[CheckList['CheckItem']][0]) >= 8:
                            if LinkDataitem[CheckList['CheckItem']][0][:8] == 'Inherit:':
                                self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,
                                     Rule_ID, 'Please manually check whether the properties of block \"'+BlockName+'\" in system \"'+Name+'\"complies with the rule')
                                proceed = False

                        if proceed == True:

                            if CheckList['CheckExp'] == 'GREATER/EQUAL':
                                try:
                                    if int(LinkDataitem[CheckList['CheckItem']][0]) >= CheckList['CheckValue']:
                                        self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                             Rule_ID, 'Block property \"'+CheckList['CheckItem']+'\" value \"'+ LinkDataitem[CheckList['CheckItem']][0] + '\" in bock \"'+BlockName+'\" of system \"'+Name+'\"complies with the rule')
                                    else:
                                        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                             Rule_ID, 'Block property \"'+CheckList['CheckItem']+'\" value \"'+ LinkDataitem[CheckList['CheckItem']][0] + '\" in bock \"'+BlockName+'\" of system \"'+Name+'\"does not comply with the rule')
                                except:
                                    self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,
                                         Rule_ID, 'Please manually check whether the pproperty \"'+CheckList['CheckItem']+'\" of block \"'+BlockName+'\" in system \"'+Name+'\"complies with the rule')

                            elif CheckList['CheckExp'] == 'OTHERTHAN':
                                if LinkDataitem[CheckList['CheckItem']][0] not in CheckList['CheckValue']:
                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                         Rule_ID, 'Block property \"'+CheckList['CheckItem']+'\" value \"'+ LinkDataitem[CheckList['CheckItem']][0] + '\" in bock \"'+BlockName+'\" of system \"'+Name+'\"complies with the rule')
                                else:
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                         Rule_ID, 'Block property \"'+CheckList['CheckItem']+'\" value \"'+ LinkDataitem[CheckList['CheckItem']][0] + '\" in bock \"'+BlockName+'\" of system \"'+Name+'\"does not comply with the rule')

                            elif CheckList['CheckExp'] == 'NOT EQUAL':
                                if LinkDataitem[CheckList['CheckItem']][0] != CheckList['CheckValue']:
                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                         Rule_ID, 'Block property \"'+CheckList['CheckItem']+'\" value \"'+ LinkDataitem[CheckList['CheckItem']][0] + '\" in bock \"'+BlockName+'\" of system \"'+Name+'\"complies with the rule')
                                else:
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                         Rule_ID, 'Block property \"'+CheckList['CheckItem']+'\" value \"'+ LinkDataitem[CheckList['CheckItem']][0] + '\" in bock \"'+BlockName+'\" of system \"'+Name+'\"does not comply with the rule')
                            elif CheckList['CheckExp'] == 'WITHIN':
                                if LinkDataitem[CheckList['CheckItem']][0] in CheckList['CheckValue']:
                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                         Rule_ID, 'Block property \"'+CheckList['CheckItem']+'\" value \"'+ LinkDataitem[CheckList['CheckItem']][0] + '\" in bock \"'+BlockName+'\" of system \"'+Name+'\"complies with the rule')
                                else:
                                    self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                         Rule_ID, 'Block property \"'+CheckList['CheckItem']+'\" value \"'+ LinkDataitem[CheckList['CheckItem']][0] + '\" in bock \"'+BlockName+'\" of system \"'+Name+'\"does not comply with the rule')
                    else:
                        self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,
                             Rule_ID, 'Please manually check whether the properties of block \"'+BlockName+'\" complies with the rule')
            inpLst, foundLst, Name = self._getNextList()

    #-------------------------------------------------------------------------------------------
    def NonEmptyStringForInOutport_RCAPI(self, RULE_ID, PropDic, ListType, CheckType, ExceptionModule = []):
        BlockList = []
        SrcBlockLineList  = []
        DstBlockLineList  = []
        SystemInfoList = []
        SystemInfoList = self.IndividualSystemData
        if self.ModuleName not in ExceptionModule:
            for IndexOfSystem in range(0,len(SystemInfoList)):
                srchKeys = ['BlockType','Name']
                BlockDataInSystem  = self._getSrchDataFromSubBlck_RCAPI(SystemInfoList[IndexOfSystem], 'Block', srchKeys)
                BlockDict=list(BlockDataInSystem)
                if  len(BlockDict[0])!=0:
                    #fetch SrcName and Name from all Line
                    srchKeys = ['Name',PropDic['SourceProp']]
                    LineDataInSystem  = self._getSrchDataFromSubBlck_RCAPI(SystemInfoList[IndexOfSystem], 'Line', srchKeys)
                    SrcBlockLineList = list(LineDataInSystem)
                    NamesList = []
                    # Fetch the Block details, which have BlockType and store those Blocks in NamesList

                    for SearchItemForBlock in range(0,len(BlockDict)):
                        if BlockDict[SearchItemForBlock]['BlockType'][0]  == PropDic['BlockType']:
                            NamesList.append(BlockDict[SearchItemForBlock]['Name'][0])

                    # compare NameList property with  SourceProp in Line.if it matches then check for Name is null property
                    for  SearchItemForList in range(0,len(SrcBlockLineList)):
                        if PropDic['SourceProp'] in SrcBlockLineList[SearchItemForList].keys():
                            for SearchItem in range(0,len(NamesList)):
                                if  SrcBlockLineList[SearchItemForList][PropDic['SourceProp']][0] ==  NamesList[SearchItem]:
                                    if CheckType == 'Exist':
                                        if 'Name' in SrcBlockLineList[SearchItemForList].keys():
                                            #Compare Name property in Line with Null('')
                                            if SrcBlockLineList[SearchItemForList]['Name'][0] == '' :
                                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,RULE_ID,
                                                     'The value of property \"'+'Name'+'\" in \"'+ListType[0]+'" with \"'+PropDic['SourceProp']+'" equals to\"'+SrcBlockLineList[SearchItemForList][PropDic['SourceProp']][0]+'\" is empty string')
                                            else:
                                                self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                     RULE_ID, 'The value of property \"'+'Name'+'\" in \"'+ListType[0]+'" with\"'+PropDic['SourceProp']+'\" equals to\"'+SrcBlockLineList[SearchItemForList][PropDic['SourceProp']][0]+'\" in List  is not empty string')
                                        else:
                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                 RULE_ID, 'Name property does not exist in \"'+ListType[0]+'" with \"'+PropDic['SourceProp']+'" equals to \"'+SrcBlockLineList[SearchItemForList][PropDic['SourceProp']][0]+'\"')

                                    elif CheckType == 'Exact':
                                        if 'Name' in SrcBlockLineList[SearchItemForList].keys():
                                            #Compare Name property in Line with Srcblk

                                            if SrcBlockLineList[SearchItemForList]['Name'][0] == SrcBlockLineList[SearchItemForList][PropDic['SourceProp']][0]:
                                                 self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,RULE_ID,
                                                     'The value of property \"'+'Name'+'\" in \"'+ListType[0]+'" with \"'+PropDic['SourceProp']+'" equals to\"'+SrcBlockLineList[SearchItemForList][PropDic['SourceProp']][0]+'\" is identical')
                                            else:
                                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                     RULE_ID, 'The value of property \"'+'Name'+'\" in \"'+ListType[0]+'" with\"'+PropDic['SourceProp']+'\" equals to\"'+SrcBlockLineList[SearchItemForList][PropDic['SourceProp']][0]+'\" in List  is not identical')
                                        else:
                                            self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                 RULE_ID, 'Name property does not exist in \"'+ListType[0]+'" with \"'+PropDic['SourceProp']+'" equals to \"'+SrcBlockLineList[SearchItemForList][PropDic['SourceProp']][0]+'\"')

        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

	#-------------------------------------------------------------------------------------------
    '''
       MANUAL CHECK RULE:
                        This API gives the information about where exactly we need to check
                        the Block manually
    '''
    def checkInputPrpty_RCAPI(self,Rule_ID,srchKeys,outputInfo,ruleType,ExceptionModule = []):
        if self.ModuleName not in ExceptionModule:
            # Get the reuseable blocks used in the model under check
            inpLst, foundLst, Name= self._getNextList()
            while (foundLst == True):
                GetStats, PropDict, rSubLst, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Block', srchKeys.keys())
                for srchIndx in range(0,len(PropDict)):
                    if ruleType == 'MathExist':
                        if PropDict[srchIndx]['BlockType'] == srchKeys['BlockType']:
                            if 'Operator' in PropDict[srchIndx].keys():
                                if PropDict[srchIndx]['Operator'] in srchKeys['Operator']:
                                    resMsg = outputInfo[0]+Name+'/'+PropDict[srchIndx]['Name']+'. '+outputInfo[1]
                                    self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,Rule_ID,resMsg)
                    else:
                        if ruleType == 'ProductExist':
                            if PropDict[srchIndx]['BlockType'] == srchKeys['BlockType']:
                                if Rule_ID == 'HISL_0005 A':
                                    if 'Multiplication' not in PropDict[srchIndx].keys():
                                        if 'Inputs' in PropDict[srchIndx].keys():
                                            if '/' in PropDict[srchIndx]['Inputs']:
                                                resMsg = outputInfo[0]+Name+'/'+PropDict[srchIndx]['Name']+'. '+outputInfo[1]
                                                self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,Rule_ID,resMsg)
                                    else:
                                        if PropDict[srchIndx]['Multiplication'] != 'Matrix(*)':
                                            if 'Inputs' in PropDict[srchIndx].keys():
                                                if '/' in PropDict[srchIndx]['Inputs']:
                                                    resMsg = outputInfo[0]+Name+'/'+PropDict[srchIndx]['Name']+'. '+outputInfo[1]
                                                    self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,Rule_ID,resMsg)
                                else:
                                    if Rule_ID == 'HISL_0005 B':
                                        if 'Multiplication'  in PropDict[srchIndx].keys():
                                            if PropDict[srchIndx]['Multiplication'] == 'Matrix(*)':
                                                if 'Inputs' in PropDict[srchIndx].keys():
                                                    if '/' in PropDict[srchIndx]['Inputs']:
                                                        resMsg = outputInfo[0]+Name+'/'+PropDict[srchIndx]['Name']+'. '+outputInfo[1]
                                                        self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,Rule_ID,resMsg)
                        else:
                            if ruleType == 'blockExist':
                                if PropDict[srchIndx]['BlockType'] == srchKeys['BlockType']:
                                    resMsg = outputInfo[0]+Name+'/'+PropDict[srchIndx]['Name']+' '+outputInfo[1]
                                    self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,Rule_ID,resMsg)
                            else:
                                if ruleType == 'Exist':
                                    if Rule_ID == 'HISL_0016 A':
                                        if PropDict[srchIndx]['BlockType'] == srchKeys['BlockType']:
                                            if 'Operator' in PropDict[srchIndx].keys():
                                                if PropDict[srchIndx]['Operator'] in srchKeys['Operator']:
                                                    resMsg = outputInfo[0]+Name+'/'+PropDict[srchIndx]['Name']+' '+outputInfo[1]
                                                    self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,Rule_ID,resMsg)
                                    else:
                                        if Rule_ID == 'HISL_0019 A':
                                            if PropDict[srchIndx]['BlockType'] == srchKeys['BlockType']:
                                                if 'SourceType' in PropDict[srchIndx].keys():
                                                    if PropDict[srchIndx]['SourceType'] in srchKeys['SourceType']:
                                                        resMsg = outputInfo[0]+Name+'/'+PropDict[srchIndx]['Name']+' '+outputInfo[1]
                                                        self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,Rule_ID,resMsg)
                                else:
                                    if ruleType == 'Dynamic':
                                        if PropDict[srchIndx]['BlockType'] in srchKeys['BlockType']:
                                            resMsg = outputInfo[0]+Name+'/'+PropDict[srchIndx]['Name']+' '+outputInfo[1]										
                                            if PropDict[srchIndx]['BlockType'] == 'Reference':				
                                                if 'SourceType' in PropDict[srchIndx].keys():
                                                    if PropDict[srchIndx]['SourceType'] == srchKeys['SourceType']:							 
                                                        self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,Rule_ID,resMsg)	
                                            else: 											
                                                self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,Rule_ID,resMsg)	
                inpLst, foundLst, Name= self._getNextList()
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')


    #-------------------------------------------------------------------------------------------
    def ManualCheck_RCAPI(self,Rule_ID,resultInfo,ExceptionModule = []):
        '''__MDLlist
        '''
        if self.ModuleName not in ExceptionModule:
            srchKeys = ['SimCustomSourceCode','SimCustomHeaderCode','SimCustomInitializer','SimCustomTerminator','SimUserSources','SimUserIncludeDirs','SimUserLibraries']		
            CCGetStats,CCPropDict,CCrSubLst,CCCompltLst = self._getSrchDataFromBlck_RCAPI(self.__MDLlist, 'Simulink.SFSimCC',srchKeys)
            if len(CCPropDict[0])==0:
                self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                    Rule_ID,'C code has not defined in Custom code tab')			
            else: 			
                if 'SimCustomSourceCode' in CCPropDict[0].keys() or 'SimCustomHeaderCode' in CCPropDict[0].keys() or 'SimCustomInitializer' in CCPropDict[0].keys() or 'SimCustomTerminator' in CCPropDict[0].keys() or 'SimUserSources' in CCPropDict[0].keys() or 'SimUserIncludeDirs' in CCPropDict[0].keys() or 'SimUserLibraries' in CCPropDict[0].keys():			
                    self.dataLoggerObj.logCondResult("-", "-", "MANUAL", "::", self.ModuleName,
                         Rule_ID,'\"'+resultInfo[0]+'"') 
        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

        		
    	
    #-------------------------------------------------------------------------------------------	
    def checkBusSignals_RCAPI(self,Rule_ID,resultType,ExceptionModule = []):
        '''
        '''
        if self.ModuleName not in ExceptionModule:
            if resultType == 'Match':
                inpLst, foundLst, Name= self._getNextList()
                while (foundLst == True):
                    GetStats, PropDict, rSubLst, CompltLst = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Block',['BlockType','Name','OutDataTypeStr'])
                    GetStats2, PropDict2, rSubLst2, CompltLst2 = self._getSrchDataFromBlck_RCAPI(inpLst['List'], 'Line',['SrcBlock','DstBlock','Name'])
                    for srchKey in range(0,len(PropDict)):
                        if PropDict[srchKey]['BlockType'] == 'BusCreator':
                            nameOfBlock = PropDict[srchKey]['Name']
                            for srchPos in range(0,len(PropDict2)):
                                if 'SrcBlock' in PropDict2[srchPos].keys():
                                    if PropDict2[srchPos]['SrcBlock'] == nameOfBlock:
                                        names = {}
                                        names['BlockName'] = nameOfBlock
                                        if 'Name' in PropDict2[srchPos].keys():
                                            names['signalName'] = PropDict2[srchPos]['Name']
                                            self.BusCreatorOutputSignalName.append(names)
                                        else:
                                            self.NotNamedOutputBuscreatorSignals.append(names)
                                if 'DstBlock' in PropDict2[srchPos].keys():
                                    if PropDict2[srchPos]['DstBlock'] == nameOfBlock:
                                        names = {}
                                        names['BlockName'] = nameOfBlock
                                        if 'Name' in PropDict2[srchPos].keys():
                                            names['signalName'] = PropDict2[srchPos]['Name']
                                            self.BusCreatorInputSignalName.append(names)
                                        else:
                                            self.NotNamedInputBusCreatorSignals.append(names)
                        else:
                            if 'OutDataTypeStr' in PropDict[srchKey].keys():
                                outputsignalName = PropDict[srchKey]['OutDataTypeStr']
                                outputsignalName=outputsignalName.split(':')
                                if outputsignalName[0] == 'Bus':
                                    nameOfBlock = PropDict[srchKey]['Name']
                                    for srchPos in range(0,len(PropDict2)):
                                        if 'SrcBlock' in PropDict2[srchPos].keys():
                                            if PropDict2[srchPos]['SrcBlock'] == nameOfBlock:
                                                names = {}
                                                names['BlockName'] = nameOfBlock
                                                if 'Name' in PropDict2[srchPos].keys():
                                                    names['signalName'] = PropDict2[srchPos]['Name']
                                                    self.BusSignals.append(names)
                                                else:
                                                    self.NotNamedBusSignal.append(names)
                        if PropDict[srchKey]['BlockType'] == 'Demux':
                            name = PropDict[srchKey]['Name']
                            for srchPos in range(0,len(PropDict2)):
                                NamesDict = {}
                                if 'DstBlock' in PropDict2[srchPos].keys():
                                    if PropDict2[srchPos]['DstBlock'] == name:
                                        if 'Name' in PropDict2[srchPos].keys():
                                            NamesDict['BlockName'] = name
                                            NamesDict['signalName'] = PropDict2[srchPos]['Name']
                                            self.deMuxInputSignalNames.append(NamesDict)
                    inpLst, foundLst, Name= self._getNextList()
                for IndxKey in range(0,len(self.BusSignals)):
                    BusSignalExist = 0
                    if len(self.BusCreatorOutputSignalName) == 0:
                       	self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                             Rule_ID,'Bus Creator Block is not Exist')
                        break
                    else:
                        for SrchKey in range(0,len(self.BusCreatorOutputSignalName)):
                            if self.BusSignals[IndxKey]['signalName'] == self.BusCreatorOutputSignalName[SrchKey]['signalName']:
                       	        self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                     Rule_ID,'BusSignal:\"'+self.BusSignals[IndxKey]['signalName']+'" of Block:\"'+self.BusSignals[IndxKey]['BlockName']+'" is created by BusCreator:\"'+self.BusSignals[IndxKey]['BlockName']+'".')
                                BusSignalExist = 1
                        if BusSignalExist == 0:
                  	        self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                 Rule_ID,'BusSignal:\"'+self.BusSignals[IndxKey]['signalName']+'" of Block:\"'+self.BusSignals[IndxKey]['BlockName']+'" has not created by BusCreator.')
                if len(self.BusSignals) == 0 and len(self.BusCreatorOutputSignalName) == 0:
                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                         Rule_ID,'Bus Signals are is not Exist')
                else:
                    if 	len(self.BusCreatorOutputSignalName)>0:
                        for indx in range(0,len(self.BusCreatorOutputSignalName)):
                            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                 Rule_ID,'Bus Signal:\"'+self.BusCreatorOutputSignalName[indx]['signalName']+'" is output of BusCreator Block:\"'+self.BusCreatorOutputSignalName[indx]['BlockName']+'"')

            else:
                if resultType == 'Exist':
                    if len(self.BusSignals) == 0 and len(self.BusCreatorOutputSignalName) == 0:
                        self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                             Rule_ID,'Bus Signals are is not Exist')
                    else:
                        if len(self.NotNamedBusSignal) == 0 and len(self.NotNamedOutputBuscreatorSignals) == 0:
                            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                 Rule_ID,'All Bus signal outPut names are named')
                        else:
                            for indexPos in range(0,len(self.NotNamedBusSignal)):
                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                     Rule_ID,'Output signal of Block:\"'+self.NotNamedBusSignal[indexPos]['BlockName']+'" should be named')
                            for indexPos in range(0,len(self.NotNamedOutputBuscreatorSignals)):
                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                     Rule_ID,'Output signal of Block:\"'+self.NotNamedOutputBuscreatorSignals[indexPos]['BlockName']+'" should be named')
                else:
                    if resultType == 'NameExist':
                        if len(self.NotNamedInputBusCreatorSignals)==0:
                            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                 Rule_ID,'Input Signals of all busCreator Block has named')
                        else:
                            for srckKey in range(0,len(self.NotNamedInputBusCreatorSignals)):
                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                     Rule_ID,'Must name the all input signals of BusCreator:\"'+self.NotNamedInputBusCreatorSignals[srckKey]['BlockName']+'"')
                    else:
                        if resultType == 'NotExist':
                            if len(self.deMuxInputSignalNames) == 0:
                                self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                     Rule_ID,'DeMux Block Not exist')
                            else:
                                if len(self.BusCreatorOutputSignalName) == 0 and len(self.BusSignals) == 0:
                                    self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                         Rule_ID,'Model file does not have bus Signal')
                                else:
                                    BusSignalExist = False
                                    busSignal = self.BusSignals
                                    for busIndexer in range(0,len(self.BusCreatorOutputSignalName)):
                                        searchKeyExist = False
                                        for busIndexer2 in range(0,len(self.BusSignals)):
                                            if self.BusCreatorOutputSignalName[busIndexer]['signalName'] in self.BusSignals[busIndexer2].values() :
                                            	searchKeyExist = True
                                        if searchKeyExist == False:
                                            busSignal.append(self.BusCreatorOutputSignalName[busIndexer])
                                    for busIndexer in range(0,len(busSignal)):
                                        for deMuxInderer in range(0,len(self.deMuxInputSignalNames)):
                                            if busSignal[busIndexer]['signalName'] == self.deMuxInputSignalNames[deMuxInderer]['signalName']:
                                                self.dataLoggerObj.logCondResult("-", "-", "FAIL", "::", self.ModuleName,
                                                     Rule_ID,'Bus :\"'+busSignal[busIndexer]['signalName']+'" Must only be split up using BusSelector Block Not Demux Block:\"'+self.deMuxInputSignalNames[deMuxInderer]['BlockName']+'"')
                                                BusSignalExist = True
                                    if BusSignalExist == False:
                                        self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                                                 Rule_ID,'None of the Bus signal Splitted using Demux Block')

        else:
            self.dataLoggerObj.logCondResult("-", "-", "PASS", "::", self.ModuleName,
                 Rule_ID, 'Rule Check is excluded in this Module')

    def processAllRulesC(self):
        # RULE __________________________________________________________________________________
        RULE_ID = ''
        #Configuration Settings Check, MISRA AC SLSF 003 and MISRA AC SLSF 004
        self.checkCCSettings_RCAPI()

        if MISRACheckbox == True:

            # RULE __________________________________________________________________________________
			
            RULE_ID = 'MISRA AC SLSF 005 B'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkEMLBlockdonotExist_RCAPI(RULE_ID,Input['ResultType'],['Null'])

            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 005 C'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            #TODO specify the fault logging module name to exculde
            self.checkPropDoNotExists_RCAPI(RULE_ID, Input['Model'], Input['Property'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 006 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkInputPrpty_RCAPI(RULE_ID, Input['srchKeys'],Input['RuleInfo'],Input['matchType'])

            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 007 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkSystemPropValueInBlock_RCAPI(RULE_ID, Input['PropChkData'], Input['UniqueKey'], [], [], 'NEGATIVE')
            self.checkSystemPropValueInBlock_RCAPI(RULE_ID, Input['PropChkData1'], Input['UniqueKey'], [], [], 'NEGATIVE')
            self.checkSystemPropValueInBlock_RCAPI(RULE_ID, Input['PropChkData2'], Input['UniqueKey'], [], [], 'NEGATIVE')
            self.checkSystemPropValueInBlock_RCAPI(RULE_ID, Input['PropChkData3'], Input['UniqueKey'], [], [], 'NEGATIVE')
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 008 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkSystemPropValueInBlock_RCAPI(RULE_ID, Input['PropChkData'], Input['UniqueKey'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 008 B'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkSystemPropValueInBlock_RCAPI(RULE_ID, Input['PropChkData'], Input['UniqueKey'], Input['ExcludeBlockLst'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 009 B'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkPropDoNotExists_RCAPI(RULE_ID, Input['Model'], Input['Property'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 009 D'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkSystemPropValueInBlock_RCAPI(RULE_ID, Input['PropChkData1'], Input['UniqueKey'], Input['ExcludeBlockLst'])
            self.checkPropValueByBlockType_RCAPI(RULE_ID, Input['ListType'], Input['PropChkData2'], Input['BlockType1'], Input['UniqueKey'], Input['ResultMatchType'], Input['ExcludeBlockLst'])
            self.checkPropValueByBlockType_RCAPI(RULE_ID, Input['ListType'], Input['PropChkData2'], Input['BlockType2'], Input['UniqueKey'], Input['ResultMatchType'], Input['ExcludeBlockLst'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 011 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkSrcDataByLink_RCAPI(RULE_ID, Input['SrcInput'], Input['DstInput'], Input['CheckList'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 011 B'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkSystemPropValueInBlock_RCAPI(RULE_ID, Input['PropChkData'], Input['UniqueKey'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 012'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkTagNameAndSignalOrBusMustMatch_RCAPI(RULE_ID, Input['PropChkData'], Input['UniqueKey'], Input['ResultMatchType'],[])
            # RULE __________________________________________________________________________________


            RULE_ID = 'MISRA AC SLSF 013 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkPropValueByBlockType_RCAPI(RULE_ID, Input['ListType'], Input['PropChkData'], Input['BlockType'], Input['UniqueKey'], Input['ResultMatchType'], [])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 013 C'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkInputPrpty_RCAPI(RULE_ID, Input['srchKeys'],Input['RuleInfo'],Input['matchType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 016 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkBusSignals_RCAPI(RULE_ID,Input['matchType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 016 B'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkBusSignals_RCAPI(RULE_ID,Input['matchType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 016 C'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkBusSignals_RCAPI(RULE_ID,Input['matchType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 016 E'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkBusSignals_RCAPI(RULE_ID,Input['matchType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 017 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkNoUnconnectedBlocks_RCAPI(RULE_ID, Input['ListType'], Input['AllowedBlock'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 017 B'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkPropValueInLinkData_RCAPI(RULE_ID, self.__SystemBlock[0]['LinkData'], Input['ResultMatchType'], Input['PropChkData'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 018 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.chkPropValByCond_RCAPI(RULE_ID, Input['ListType'], Input['PropData'], Input['CheckListData'])
            self.checkBlckPropValueInOtherBlock_RCAPI(RULE_ID, Input['PropChkData'], Input['UniqueKey'], Input['ResultMatchType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 018 B'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkTagNameAndSignalOrBusMustMatch_RCAPI(RULE_ID, Input['PropChkData'], Input['UniqueKey'], Input['ResultMatchType'],[])
            # RULE __________________________________________________________________________________


            RULE_ID = 'MISRA AC SLSF 018 C'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkForDuplicatePropInBlocks_RCAPI(RULE_ID, Input['PropChkData'], Input['UniqueKey'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 018 D'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkBlckPropValueInOtherBlock_RCAPI(RULE_ID, Input['PropChkData'], Input['UniqueKey'], Input['ResultMatchType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 018 E'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkBlckPropValueInOtherBlock_RCAPI(RULE_ID, Input['PropChkData'], Input['UniqueKey'], Input['ResultMatchType'])
            # RULE __________________________________________________________________________________
            RULE_ID = 'MISRA AC SLSF 027 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkPropValueInLinkData_RCAPI(RULE_ID, self.__SystemBlock[0]['LinkData'], Input['ResultMatchType'], Input['PropChkData'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 027 C'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.NonEmptyStringForInOutport_RCAPI(RULE_ID,Input['PropChkData'],Input['ListType'], Input['ResultMatchType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 027 D'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.NonEmptyStringForInOutport_RCAPI(RULE_ID,Input['PropChkData'],Input['ListType'], Input['ResultMatchType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 027 E'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkReusableLib_RCAPI(RULE_ID, Input['srchKeys'], Input['PropChkData'])
            # RULE _________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 027 G'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkTagNameAndSignalOrBusMustMatch_RCAPI(RULE_ID, Input['PropChkData'], Input['UniqueKey'], Input['ResultMatchType'],Input['AllowedBlock'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 027 I'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.NonEmptyStringForInOutport_RCAPI(RULE_ID,Input['PropChkData'], Input['ListType'], Input['ResultMatchType'])
            self.NonEmptyStringForInOutport_RCAPI(RULE_ID,Input['PropChkData1'], Input['ListType'], Input['ResultMatchType'])
            self.NonEmptyStringForInOutport_RCAPI(RULE_ID,Input['PropChkData2'], Input['ListType'], Input['ResultMatchType'])
            self.NonEmptyStringForInOutport_RCAPI(RULE_ID,Input['PropChkData3'], Input['ListType'], Input['ResultMatchType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 027 J'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkForDuplicatePropInLines_RCAPI(RULE_ID, Input['PropChkData'])
            # RULE __________________________________________________________________________________


            if len(self.__SFlist) > 0:
                RULE_ID = 'MISRA AC SLSF 034 A'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkPropValueInListType_RCAPI(RULE_ID, self.__SFlist, Input['ListType'], Input['ResultMatchType'], Input['PropChkData'], Input['ListFoundCheck'], Input['PropFoundCheck'])
                # RULE __________________________________________________________________________________

                RULE_ID = 'MISRA AC SLSF 034 C'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkPropValueInListType_RCAPI(RULE_ID, self.__SFlist, Input['ListType'], Input['ResultMatchType'], Input['PropChkData'], Input['ListFoundCheck'], Input['PropFoundCheck'])
                # RULE __________________________________________________________________________________

                RULE_ID = 'MISRA AC SLSF 034 D'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkPropValueInListType_RCAPI(RULE_ID, self.__SFlist, Input['ListType'], Input['ResultMatchType'], Input['PropChkData'])
                # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 035 B'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkPropDoNotExists_RCAPI(RULE_ID, Input['Model'], Input['Property'])
            # RULE __________________________________________________________________________________

            if len(self.__SFlist) > 0:

                RULE_ID = 'MISRA AC SLSF 036 A'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkNoInputBusSignalForSFBlocks_RCAPI(RULE_ID,Input['srchKeys']['LineSrchKeys'],Input['srchKeys']['BlckSrchKeys'],Input['srchKeys']['chartSrchKeys'])
                # RULE __________________________________________________________________________________

                RULE_ID = 'MISRA AC SLSF 036 C'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkSignalLableAndPortNameShouldMatch_RCAPI(RULE_ID,Input['srchKeys']['BlckSrchKeys'],Input['srchKeys']['chartSrchKeys'])
                # RULE __________________________________________________________________________________

                RULE_ID = 'MISRA AC SLSF 037 G'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkDataItemInOtherSFBlocks_RCAPI(RULE_ID, Input['PropChkData'])
                # RULE __________________________________________________________________________________

                RULE_ID = 'MISRA AC SLSF 037 H'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkPropValueInListType_RCAPI(RULE_ID, self.__SFlist, Input['ListType'], Input['ResultMatchType'], Input['PropChkData'])
                # RULE __________________________________________________________________________________

                RULE_ID = 'MISRA AC SLSF 039 A'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkEMLBlockdonotExist_RCAPI(RULE_ID,Input['ResultType'],self.__SFlist)
                # RULE __________________________________________________________________________________

                RULE_ID = 'MISRA AC SLSF 041 A'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkPropValueInListType_RCAPI(RULE_ID, self.__SFlist, Input['ListType'], Input['ResultMatchType'], Input['PropChkData'])

                RULE_ID = 'MISRA AC SLSF 042 A'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkTransitionProperties_RCAPI(RULE_ID, self.__SFlist,Input['resultType'])

                RULE_ID = 'MISRA AC SLSF 042 B'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkTransitionProperties_RCAPI(RULE_ID, self.__SFlist,Input['resultType'])

                RULE_ID = 'MISRA AC SLSF 042 C'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkTransitionProperties_RCAPI(RULE_ID, self.__SFlist,Input['resultType'])
				
                RULE_ID = 'MISRA AC SLSF 042 D'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkTransitionProperties_RCAPI(RULE_ID, self.__SFlist,Input['resultType'])

                RULE_ID = 'MISRA AC SLSF 042 E'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkTransitionProperties_RCAPI(RULE_ID, self.__SFlist,Input['resultType'])

                RULE_ID = 'MISRA AC SLSF 043 A'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkconditionalAndTransitionalAction_RCAPI(RULE_ID, self.__SFlist, Input['srchKeys'])

                RULE_ID = 'MISRA AC SLSF 043 D'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkForSemiColonInActions_RCAPI(RULE_ID, Input['ChkData'])
                # RULE __________________________________________________________________________________
				
                RULE_ID = 'MISRA AC SLSF 043 I'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkTransitionProperties_RCAPI(RULE_ID, self.__SFlist,Input['resultType'])

            if len(self.__SFlist) > 0:
                RULE_ID = 'MISRA AC SLSF 043 J'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkTemporalInOtherSFBlocks_RCAPI(RULE_ID, Input['ChkData'])
                # RULE __________________________________________________________________________________

                RULE_ID = 'MISRA AC SLSF 044 A'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkPropValueInListType_RCAPI(RULE_ID, self.__SFlist, Input['ListType'], Input['ResultMatchType'], Input['PropChkData'])
                # RULE __________________________________________________________________________________

                RULE_ID = 'MISRA AC SLSF 044 C'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkForActionsInFlowcharts_RCAPI(RULE_ID, Input['ChkData'])
                # RULE __________________________________________________________________________________

                RULE_ID = 'MISRA AC SLSF 046 A'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkPropValueInListType_RCAPI(RULE_ID, self.__SFlist, Input['ListType'], Input['ResultMatchType'], Input['PropChkData'])
                # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 048 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkPropDoNotExists_RCAPI(RULE_ID, Input['Model'], Input['Property'])
            # RULE __________________________________________________________________________________

            if len(self.__SFlist) > 0:
			
                RULE_ID = 'MISRA AC SLSF 048 C'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.ManualCheck_RCAPI(RULE_ID,Input['RuleInfo'])
                # RULE __________________________________________________________________________________
    			
                RULE_ID = 'MISRA AC SLSF 048 D'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.ManualCheck_RCAPI(RULE_ID,Input['RuleInfo'])
                # RULE __________________________________________________________________________________

                RULE_ID = 'MISRA AC SLSF 048 E'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.ManualCheck_RCAPI(RULE_ID,Input['RuleInfo'])
                # RULE __________________________________________________________________________________

                RULE_ID = 'MISRA AC SLSF 048 F'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.ManualCheck_RCAPI(RULE_ID,Input['RuleInfo'])
                # RULE __________________________________________________________________________________

                RULE_ID = 'MISRA AC SLSF 048 B'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkEMLBlockdonotExist_RCAPI(RULE_ID,Input['ResultType'],self.__SFlist)
                # RULE __________________________________________________________________________________

                RULE_ID = 'MISRA AC SLSF 048 G'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkPropValueInListType_RCAPI(RULE_ID, self.__SFlist, Input['ListType'], Input['ResultMatchType'], Input['PropChkData'], Input['ListFoundCheck'], Input['PropFoundCheck'])
                self.checkPropValueInListType_RCAPI(RULE_ID, self.__SFlist, Input['ListType1'], Input['ResultMatchType'], Input['PropChkData'], Input['ListFoundCheck'], Input['PropFoundCheck'])
                # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 052 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkForDuplicatePropInSFBlocks_RCAPI(RULE_ID, Input['PropChkData'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'MISRA AC SLSF 052 B'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkBlckPropValueInOtherSFBlock_RCAPI(RULE_ID, Input['PropChkData'], Input['CheckType'])
            # RULE __________________________________________________________________________________

            if len(self.__SFlist) > 0:
			
                RULE_ID = 'MISRA AC SLSF 053 A'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkTransitionProperties_RCAPI(RULE_ID, self.__SFlist,Input['resultType'])
			
                RULE_ID = 'MISRA AC SLSF 055 A'
                self.checkForOrderOfActions_RCAPI()
                # RULE __________________________________________________________________________________
            
			#Manual checking Rule Information				
            self.dataLoggerObj.ManualCheckRulesInfo()
			
            RULE_ID = 'MISRA AC SLSF 005 B'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'Only Data type conversion block must be used where signal data type conversion is required.')				

            RULE_ID = 'MISRA AC SLSF 006 B'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'Block parameters intended to be configured or calibrated must be entered as named constants.')				

            RULE_ID = 'MISRA AC SLSF 006 D'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'named constants in Block Parameters must be Defined in External file eg:m-file,spread-sheet,data dictionary')				

            RULE_ID = 'MISRA AC SLSF 006 E'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'Masked sub-systems must not be used to pass parameters')				
			
            RULE_ID = 'MISRA AC SLSF 009 C'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'Execution order specified by function calls or data flows.')				

            RULE_ID = 'MISRA AC SLSF 015 A'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'Vector signal:created either by feeding individual named scalar signals into a mux-block, or by using a vector constant, or by a Stateflow block.')				

            RULE_ID = 'MISRA AC SLSF 015 B'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'Matrix signal:created either by feeding individual vector signals into a matrix concatenation block, or a matrix constant, or by a Stateflow block.')				

            RULE_ID = 'MISRA AC SLSF 015 C'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'contain signals with common functionality, data type, dimensions and units.')				

            RULE_ID = 'MISRA AC SLSF 027 B'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'Propagated labels must be used to redisplay the names of previously labelled signal or bus on all sub-sequent usage of signal flow.')				

            RULE_ID = 'MISRA AC SLSF 035 A'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'The choice of state-chart or flow-chart is driven by the nature of the behaviour being modelled.')				

            RULE_ID = 'MISRA AC SLSF 037 A'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'All data of StateFlow Block Must be defined at the chart level or below in the object hierarchy and not at the model level.')				

            RULE_ID = 'MISRA AC SLSF 037 B'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'local data item name must not be used in different scopes within one state machine.')				

            RULE_ID = 'MISRA AC SLSF 038 C'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'C library functions must not be used in a state machine. ')				

            RULE_ID = 'MISRA AC SLSF 040 B'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'Parent of the parallel state must not be a parallel state in stateChart')				

            RULE_ID = 'MISRA AC SLSF 040 D'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'the order of the critical states must be documented in a textbox at the top level of the state machine, wherever critical.')				

            RULE_ID = 'MISRA AC SLSF 043 F'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'no more than one internal transition from any state in StateChart')				

            RULE_ID = 'MISRA AC SLSF 047 A'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'local , directed, broadcasted stateflow events, including all implicit eventsmust not be used.')				

            RULE_ID = 'MISRA AC SLSF 047 B'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'output sateflows must be used only as outputs and not tested internally on transition conditions.')				

            RULE_ID = 'MISRA AC SLSF 053 J'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'In all FlowCharts,graphical functions ,there must be only one terminating junction.')				

            RULE_ID = 'MISRA AC SLSF 054 A'
            self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'Transition labels must be positioned so there is no ambiguity which transition they apply to')				

        if Hi_intCheckbox == True:

            RULE_ID = 'HISL_0002 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkSrcDataByLink_RCAPI(RULE_ID, Input['SrcInput'], Input['DstInput'], Input['CheckList'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'HISL_0002 B'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkInputPrpty_RCAPI(RULE_ID, Input['srchKeys'],Input['RuleInfo'],Input['matchType'])
            # RULE __________________________________________________________________________________

            if len(self.__SFlist) > 0:
                RULE_ID = 'HISF_0003 A'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkSrcDataByLink_RCAPI(RULE_ID, Input['SrcInput'], Input['DstInput'], Input['CheckList'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'HISL_0003 C'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkSrcDataByLink_RCAPI(RULE_ID, Input['SrcInput'], Input['DstInput'], Input['CheckList'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'HISL_0004 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkInputPrpty_RCAPI(RULE_ID, Input['srchKeys'],Input['RuleInfo'],Input['matchType'])

            # RULE __________________________________________________________________________________
            RULE_ID = 'HISL_0004 B'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkInputPrpty_RCAPI(RULE_ID, Input['srchKeys'],Input['RuleInfo'],Input['matchType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'HISL_0005 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkInputPrpty_RCAPI(RULE_ID, Input['srchKeys'],Input['RuleInfo'],Input['matchType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'HISL_0005 B'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkInputPrpty_RCAPI(RULE_ID, Input['srchKeys'],Input['RuleInfo'],Input['matchType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'HISL_0005 C'
            self.checkdebuggCC_RCAPI(RULE_ID)
            # RULE __________________________________________________________________________________

            RULE_ID = 'HISL_0010 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkPropValueByBlockType_RCAPI(RULE_ID, Input['ListType'], Input['PropChkData'], Input['BlockType'], Input['UniqueKey'], Input['ResultMatchType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'HISL_0010 B'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkOutputshouldConnectActionPort_RCAPI(RULE_ID, Input['blockType'], Input['PropChkData'], Input['UniqueKey'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'HISL_0011 B'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkOutputshouldConnectActionPort_RCAPI(RULE_ID, Input['blockType'], Input['PropChkData'],Input['UniqueKey'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'HISL_0011 C'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkInputPrpty_RCAPI(RULE_ID, Input['srchKeys'],Input['RuleInfo'],Input['matchType'])

            RULE_ID = 'HISL_0013 A'
            self.checkdebuggCC_RCAPI(RULE_ID)
            # RULE __________________________________________________________________________________

            RULE_ID = 'HISL_0015 B'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkInputPrpty_RCAPI(RULE_ID, Input['srchKeys'],Input['RuleInfo'],Input['matchType'])

            RULE_ID = 'HISL_0015 C'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkPropValueByBlockType_RCAPI(RULE_ID, Input['ListType'], Input['PropChkData'], Input['BlockType'], Input['UniqueKey'], Input['ResultMatchType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'HISL_0016 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkInputPrpty_RCAPI(RULE_ID, Input['srchKeys'],Input['RuleInfo'],Input['matchType'])

            RULE_ID = 'HISL_0017 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkBlockOutputType_RCAPI(RULE_ID,Input['SrchKeys'], Input['UniqueKey']['BlockType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'HISL_0018 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkBlockOutputType_RCAPI(RULE_ID,Input['SrchKeys'], Input['UniqueKey']['BlockType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'HISL_0019 A'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkInputPrpty_RCAPI(RULE_ID, Input['srchKeys'],Input['RuleInfo'],Input['matchType'])

            RULE_ID = 'HISL_0019 B'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.chkPropValByCond_RCAPI(RULE_ID, Input['ListType'], Input['PropData'], Input['CheckListData'])
            # RULE __________________________________________________________________________________

	    #Manual checking Rule Information				
            self.dataLoggerObj.ManualCheckRulesInfo()
			
            if len(self.__SFlist) > 0:
                RULE_ID = 'HISF_0010 A'
                self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'Avoid using transitions that looping out of parent of the source and destination objects')				

            if len(self.__SFlist) > 0:
                RULE_ID = 'HISF_0013 A'
                self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'Avoid creating transitions that cross from one parallel state to another.')				

            if len(self.__SFlist) > 0:
                RULE_ID = 'HISF_0014 A'
                self.dataLoggerObj.logCondResult("-", "-", "MANUAL CHECKING RULE STATUS", "::", self.ModuleName,RULE_ID,'Avoid transition paths that go into and out of a state without ending on a substate.')				
			

        if RICARDOCheckbox == True:
            # RULE __________________________________________________________________________________
            RULE_ID = 'RP_0008'
            self.checkAttributesFormatString_RCAPI()
            # RULE __________________________________________________________________________________

            RULE_ID = 'RP_0012'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkTagNameAndSignalOrBusMustMatch_RCAPI(RULE_ID, Input['PropChkData'], Input['UniqueKey'], Input['ResultMatchType'],[])
            # RULE __________________________________________________________________________________

            RULE_ID = 'RP_0018'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkSrcDataByLink_RCAPI(RULE_ID, Input['SrcInput'], Input['DstInput'], Input['CheckList'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'RP_0021'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkPropValueByBlockType_RCAPI(RULE_ID, Input['ListType'], Input['PropChkData'], Input['BlockType'], Input['UniqueKey'], Input['ResultMatchType'])
            # RULE __________________________________________________________________________________

            if len(self.__SFlist) > 0:

                RULE_ID = 'RP_0028'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkPropValue_RCAPI(RULE_ID,self.__SFlist,Input['srchKeys_chart'],Input['srchKeys_event'])
                #RULE __________________________________________________________________________________

                RULE_ID = 'RP_0036'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkPropValueInListType_RCAPI(RULE_ID, self.__SFlist, Input['ListType'], Input['ResultMatchType'], Input['PropChkData'], Input['ListFoundCheck'], Input['PropFoundCheck'])
                # RULE __________________________________________________________________________________

                RULE_ID = 'RP_0037'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkcommentSFBlocks_RCAPI(RULE_ID, Input['ChkData'])
                #RULE ________________________________________________________________________________
                RULE_ID = 'RP_0046'
                Input = DataDictionary.RuleCheckerInput[RULE_ID]
                self.checkPropValueInListType_RCAPI(RULE_ID, self.__SFlist, Input['ListType'], Input['ResultMatchType'], Input['PropChkData'])
                self.checkPropValueInListType_RCAPI(RULE_ID, self.__SFlist, Input['ListType1'], Input['ResultMatchType'], Input['PropChkData'])
                # RULE __________________________________________________________________________________

            RULE_ID = 'RP_0051'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkPropValueByBlockType_RCAPI(RULE_ID, Input['ListType'], Input['PropChkData'], Input['BlockType1'], Input['UniqueKey'], Input['ResultMatchType'])
            self.checkPropValueByBlockType_RCAPI(RULE_ID, Input['ListType'], Input['PropChkData'], Input['BlockType2'], Input['UniqueKey'], Input['ResultMatchType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'RP_0054'
            self.checkAllowedBlocks_RCAPI()
            # RULE __________________________________________________________________________________

            RULE_ID = 'RP_0055'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkPropValueInListType_RCAPI(RULE_ID, self.__SFlist, Input['ListType'], Input['ResultMatchType'], Input['PropChkData'], Input['ListFoundCheck'], Input['PropFoundCheck'])
            # RULE __________________________________________________________________________________


            RULE_ID = 'RP_0057'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkPropDoNotExists_RCAPI(RULE_ID, Input['Model'], Input['Property'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'RP_0058'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.NonEmptyStringForInOutport_RCAPI(RULE_ID,Input['PropChkData'], Input['ListType'], Input['ResultMatchType'])
            self.NonEmptyStringForInOutport_RCAPI(RULE_ID,Input['PropChkData1'], Input['ListType'], Input['ResultMatchType'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'RP_0059'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkPrtyShouldExist_RCAPI(RULE_ID,Input['PropChkData']['ECoderFlag'], Input['SrchKeys'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'RP_0060'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkPrtyShouldExist_RCAPI(RULE_ID,Input['PropChkData']['ECoderFlag'], Input['SrchKeys'])
            # RULE __________________________________________________________________________________


            RULE_ID = 'RP_0061'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkSystemPropValueInBlock_RCAPI(RULE_ID, Input['PropChkData'], Input['UniqueKey'], [], [], 'NEGATIVE')
            # RULE __________________________________________________________________________________

            RULE_ID = 'RP_0063'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkPropDoNotExists_RCAPI(RULE_ID, Input['Model'], Input['Property'])
            # RULE __________________________________________________________________________________

            RULE_ID = 'RP_0064'
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            self.checkTagNameAndSignalOrBusMustMatch_RCAPI(RULE_ID, Input['PropChkData'], Input['UniqueKey'], Input['ResultMatchType'],Input['AllowedBlock'])
            # RULE __________________________________________________________________________________
        #self.ManualCheckingRulesInfo()            


#-------------------------------------------------------------------------------------------
    # For development testing purpose
    def processAllRules(self):
            #self._Test(self.__MDLlist, 'SubSystem')

            RULE_ID = 'HISL_0002 A'
            #self.checkCCSettings_RCAPI()
            #Data  = self._getSrchDataFromSubBlck_RCAPI(self.__MDLlist, 'Simulink.CodeAppCC', PropChkData.keys())
            Input = DataDictionary.RuleCheckerInput[RULE_ID]
            for ListItem in Input:
                self.checkPropValueInListType_RCAPI(RULE_ID, self.__MDLlist, ListItem, 'Exact', Input[ListItem])

            # RULE __________________________________________________________________________________
