import datetime
import csv
import pprint
#import wx
import DataDictionary
import sys


ModelSpace = 30
RuleSpace = 30
RemarksSpace = 30


class DataLogger(object):

    # Open the file to log the data.
    def __init__( self, fileName, fPtr,filePath):
        self.__fileName = fileName
        self.filePtr = fPtr		
        csv.register_dialect('rulcheckres', delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        try:
            self.__csvAutoHandle = open(filePath+'\\'+fileName+"_Auto.csv", 'wb')
            self.__csvManHandle = open(filePath+'\\'+fileName+"_Man.csv", 'wb')
        except:
            print 'Please close all the csv files and retry!!'
            sys.exit()	
        self.__csvAutoWriter = csv.writer(self.__csvAutoHandle, 'rulcheckres')
        self.__csvManWriter = csv.writer(self.__csvManHandle, 'rulcheckres')
        self.__dispText = ''
        # self.__RuleCheckObj = RuleCheckObj
        self.__logInputFileName()
        self.RuleCheckFailed = 0

    # Close the file before the object gets destroyed.
    def __del__(self):
        self.__csvAutoHandle.close()
        self.__csvManHandle.close()


    def __logInputFileName(self):
        self.__csvAutoWriter.writerow(["File : ", self.__fileName])
        self.__csvAutoWriter.writerow(["Date :  " + str(datetime.datetime.now())])
        self.__csvAutoWriter.writerow(['Module','Rule', 'Actual Value', 'Expected Value',
                                        'PASS/FAIL Status', 'Remarks/Trace'])
        self.__csvManWriter.writerow(["File : ", self.__fileName])
        self.__csvManWriter.writerow(["Date :  " + str(datetime.datetime.now())])
        self.__csvManWriter.writerow(['Module','Rule', 'Actual Value', 'Expected Value',
                                        'PASS/FAIL Status', 'Remarks/Trace'])

    def ManualCheckRulesInfo(self):
        self.__csvAutoWriter.writerow(["MANUAL CHECKING RULES :"])

    def __resultCompare(self, rcexpdata, rcactdata, checkType = 'POSTIVE'):
        #Compare the input data with the data dictionary.
        rcretval = "FAIL"
        if checkType == 'POSTIVE':
            if rcexpdata == rcactdata:
                rcretval = "PASS"
        elif checkType == 'NEGATIVE':
            if rcexpdata != rcactdata:
                rcretval = "PASS"
        return rcretval

    def logCompResult(self, expval, actval, seperator, checkType, *arbargs):
        # arbargs should contain rulename and remarks
        PassFailStatus = self.__resultCompare(expval, actval, checkType)
        Remarks = ''
        
        if PassFailStatus == "FAIL":
            if self.RuleCheckFailed != 2:
                self.RuleCheckFailed = 1
            Remarks = seperator.join(arbargs[2:])
            RuleDetails = ''
            if arbargs[1] in DataDictionary.RuleDetails:
                RuleDetails = DataDictionary.RuleDetails[arbargs[1]]

            self.filePtr.writelines("--------------------------------------------------------------------------------------") 				
            self.filePtr.writelines("\nMODEL      >>>  %30s \n\nRULE         >>>  %30s >>> %30s\n\nREMARKS  >>>  %s \n" %((arbargs[0].ljust(30)).upper(), arbargs[1].ljust(30),
                               RuleDetails.ljust(5), Remarks.ljust(30)))

        else:
            Remarks = seperator.join(arbargs[2:-1])
        
        self.__csvAutoWriter.writerow([arbargs[0], arbargs[1], actval, expval,
                PassFailStatus, Remarks])
        self.__csvManWriter.writerow([arbargs[0], arbargs[1], actval, expval, '',
                seperator.join(arbargs[2:])])


    def logCondResult(self, expval, actval, PassFailStatus, seperator, *arbargs):
        # arbargs should contain rulename and remarks
        self.__csvAutoWriter.writerow([arbargs[0], arbargs[1], actval, expval,
            PassFailStatus, seperator.join(arbargs[2:])])

        self.__csvManWriter.writerow([arbargs[0], arbargs[1], actval, expval, '',
            seperator.join(arbargs[2:])])
        if PassFailStatus == "FAIL" or PassFailStatus == "MANUAL":
            if self.RuleCheckFailed != 2:
                self.RuleCheckFailed = 1
            if PassFailStatus == "MANUAL":
                self.RuleCheckFailed = 2
            RuleDetails = ''
            if arbargs[1] in DataDictionary.RuleDetails:
                RuleDetails = DataDictionary.RuleDetails[arbargs[1]]

            self.filePtr.writelines("--------------------------------------------------------------------------------------") 				
            self.filePtr.writelines("\nMODEL      >>>  %30s \n\nRULE         >>>  %30s >>> %30s\n\nREMARKS  >>>  %s \n" %((arbargs[0].ljust(30)).upper(), arbargs[1].ljust(30),
                               RuleDetails.ljust(5), seperator.join(arbargs[2:]).ljust(30)))
