#Boa:Frame:RuleChecker

import os

import wx
import wx.stc

import fileinput
import re
import RuleCheckerAPI
import thread
import sys

import pprint # debug purpose


def create(parent):
    return RuleChecker(parent)

[wxID_RULECHECKER, wxID_RULECHECKERBOTTONRULECHECK, 
 wxID_RULECHECKERBUTTONCANCEL, wxID_RULECHECKERBUTTONFOLDER, 
 wxID_RULECHECKERBUTTONQUIT, wxID_RULECHECKERCHECKBOXHI_INT, 
 wxID_RULECHECKERCHECKBOXMISRA, wxID_RULECHECKERCHECKBOXRICARDO, 
 wxID_RULECHECKERCHECKERPANEL, wxID_RULECHECKERGAUGEPROG, 
 wxID_RULECHECKERLISTBOX, wxID_RULECHECKERPANEL1, wxID_RULECHECKERPANEL2, 
 wxID_RULECHECKERSTATICBOX, wxID_RULECHECKERSTATICBOX1, 
 wxID_RULECHECKERSTATICLINE2, wxID_RULECHECKERSTATICTEXT1, 
 wxID_RULECHECKERSTATICTEXTMODULES, wxID_RULECHECKERSTATICTEXTPROG, 
 wxID_RULECHECKERSTATUSBAR, wxID_RULECHECKERSTMODULENAME, 
 wxID_RULECHECKERSTYLEDTEXTCTRL1, wxID_RULECHECKERTEXTCTRLFOLDER, 
 wxID_RULECHECKERTREECNTRL, 
] = [wx.NewId() for _init_ctrls in range(24)]

class RuleChecker(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_RULECHECKER, name='RuleChecker',
              parent=prnt, pos=wx.Point(17, 13), size=wx.Size(1006, 721),
              style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CLOSE_BOX | wx.CLIP_CHILDREN | wx.CAPTION,
              title='RuleChecker')
        self.SetClientSize(wx.Size(998, 687))
        self.SetToolTipString('RuleChecker')

        self.treecntrl = wx.TreeCtrl(id=wxID_RULECHECKERTREECNTRL,
              name='treecntrl', parent=self, pos=wx.Point(0, 288),
              size=wx.Size(240, 376), style=wx.TR_HAS_BUTTONS)

        self.listbox = wx.ListBox(choices=[], id=wxID_RULECHECKERLISTBOX,
              name='listbox', parent=self, pos=wx.Point(0, 16),
              size=wx.Size(240, 256), style=0)
        self.listbox.Bind(wx.EVT_LISTBOX, self.OnListboxListbox,
              id=wxID_RULECHECKERLISTBOX)

        self.Checkerpanel = wx.Panel(id=wxID_RULECHECKERCHECKERPANEL,
              name='Checkerpanel', parent=self, pos=wx.Point(240, 0),
              size=wx.Size(991, 664), style=wx.TAB_TRAVERSAL)
        self.Checkerpanel.SetToolTipString('CheckerPanel')

        self.staticBox = wx.StaticBox(id=wxID_RULECHECKERSTATICBOX,
              label='MDL Files Input', name='staticBox',
              parent=self.Checkerpanel, pos=wx.Point(16, 16), size=wx.Size(416,
              120), style=0)
        self.staticBox.SetToolTipString('')

        self.bottonRuleCheck = wx.Button(id=wxID_RULECHECKERBOTTONRULECHECK,
              label='Check', name='bottonRuleCheck', parent=self.Checkerpanel,
              pos=wx.Point(622, 38), size=wx.Size(75, 23), style=0)
        self.bottonRuleCheck.SetToolTipString('bottonRuleCheck')
        self.bottonRuleCheck.Bind(wx.EVT_BUTTON, self.OnBottonRuleCheckButton,
              id=wxID_RULECHECKERBOTTONRULECHECK)

        self.textCtrlFolder = wx.TextCtrl(id=wxID_RULECHECKERTEXTCTRLFOLDER,
              name='textCtrlFolder', parent=self.Checkerpanel, pos=wx.Point(114,
              42), size=wx.Size(304, 21), style=0, value='')
        self.textCtrlFolder.Bind(wx.EVT_KILL_FOCUS,
              self.OnTextCtrlFolderKillFocus)

        self.buttonFolder = wx.Button(id=wxID_RULECHECKERBUTTONFOLDER,
              label='Select Folder', name='buttonFolder',
              parent=self.Checkerpanel, pos=wx.Point(23, 42), size=wx.Size(75,
              23), style=0)
        self.buttonFolder.Bind(wx.EVT_BUTTON, self.OnButtonFolderButton,
              id=wxID_RULECHECKERBUTTONFOLDER)

        self.panel1 = wx.Panel(id=wxID_RULECHECKERPANEL1, name='panel1',
              parent=self, pos=wx.Point(0, 272), size=wx.Size(240, 16),
              style=wx.TAB_TRAVERSAL)

        self.panel2 = wx.Panel(id=wxID_RULECHECKERPANEL2, name='panel2',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(240, 16),
              style=wx.TAB_TRAVERSAL)

        self.staticLine2 = wx.StaticLine(id=wxID_RULECHECKERSTATICLINE2,
              name='staticLine2', parent=self, pos=wx.Point(232, 152),
              size=wx.Size(24, 504), style=0)

        self.staticText1 = wx.StaticText(id=wxID_RULECHECKERSTATICTEXT1,
              label='Module Dependency', name='staticText1', parent=self.panel1,
              pos=wx.Point(8, 0), size=wx.Size(97, 13), style=0)

        self.StaticTextModules = wx.StaticText(id=wxID_RULECHECKERSTATICTEXTMODULES,
              label='Module List', name='StaticTextModules', parent=self.panel2,
              pos=wx.Point(9, 2), size=wx.Size(53, 13), style=0)

        self.buttonCancel = wx.Button(id=wxID_RULECHECKERBUTTONCANCEL,
              label='Cancel', name='buttonCancel', parent=self.Checkerpanel,
              pos=wx.Point(622, 70), size=wx.Size(75, 23), style=0)
        self.buttonCancel.Bind(wx.EVT_BUTTON, self.OnButtonCancelButton,
              id=wxID_RULECHECKERBUTTONCANCEL)

        self.staticBox1 = wx.StaticBox(id=wxID_RULECHECKERSTATICBOX1,
              label='Rules', name='staticBox1', parent=self.Checkerpanel,
              pos=wx.Point(472, 18), size=wx.Size(264, 118), style=0)

        self.checkBoxMISRA = wx.CheckBox(id=wxID_RULECHECKERCHECKBOXMISRA,
              label='MISRA', name='checkBoxMISRA', parent=self.Checkerpanel,
              pos=wx.Point(489, 48), size=wx.Size(70, 13), style=0)
        self.checkBoxMISRA.SetValue(True)
        self.checkBoxMISRA.Bind(wx.EVT_CHECKBOX, self.OnCheckBoxMISRACheckbox,
              id=wxID_RULECHECKERCHECKBOXMISRA)

        self.checkBoxHi_int = wx.CheckBox(id=wxID_RULECHECKERCHECKBOXHI_INT,
              label='TMW Hi-Int', name='checkBoxHi_int',
              parent=self.Checkerpanel, pos=wx.Point(489, 76), size=wx.Size(70,
              13), style=0)
        self.checkBoxHi_int.SetValue(True)
        self.checkBoxHi_int.Bind(wx.EVT_CHECKBOX, self.OnCheckBoxHi_intCheckbox,
              id=wxID_RULECHECKERCHECKBOXHI_INT)

        self.checkBoxRICARDO = wx.CheckBox(id=wxID_RULECHECKERCHECKBOXRICARDO,
              label='RICARDO GL', name='checkBoxRICARDO',
              parent=self.Checkerpanel, pos=wx.Point(489, 104), size=wx.Size(96,
              13), style=0)
        self.checkBoxRICARDO.SetValue(True)
        self.checkBoxRICARDO.Bind(wx.EVT_CHECKBOX,
              self.OnCheckBoxRICARDOCheckbox,
              id=wxID_RULECHECKERCHECKBOXRICARDO)

        self.statusBar = wx.StatusBar(id=wxID_RULECHECKERSTATUSBAR,
              name='statusBar', parent=self, style=wx.CLIP_CHILDREN)
        self.statusBar.SetToolTipString('statusBar1')
        self.statusBar.SetStatusText('Status')
        self.statusBar.SetFieldsCount(3)
        self.SetStatusBar(self.statusBar)

        self.gaugeProg = wx.Gauge(id=wxID_RULECHECKERGAUGEPROG,
              name='gaugeProg', parent=self.statusBar, pos=wx.Point(792, 5),
              range=100, size=wx.Size(195, 16), style=wx.GA_HORIZONTAL)

        self.staticTextProg = wx.StaticText(id=wxID_RULECHECKERSTATICTEXTPROG,
              label='', name='staticTextProg', parent=self.statusBar,
              pos=wx.Point(689, 7), size=wx.Size(56, 13), style=0)

        self.buttonQuit = wx.Button(id=wxID_RULECHECKERBUTTONQUIT, label='Quit',
              name='buttonQuit', parent=self.Checkerpanel, pos=wx.Point(622,
              102), size=wx.Size(75, 23), style=0)
        self.buttonQuit.Bind(wx.EVT_BUTTON, self.OnButtonQuitButton,
              id=wxID_RULECHECKERBUTTONQUIT)

        self.STModuleName = wx.StaticText(id=wxID_RULECHECKERSTMODULENAME,
              label='', name='STModuleName', parent=self.statusBar,
              pos=wx.Point(344, 7), size=wx.Size(0, 13), style=0)

        self.styledTextCtrl1 = wx.TextCtrl(id=wxID_RULECHECKERSTYLEDTEXTCTRL1,
              name='styledTextCtrl1', parent=self.Checkerpanel, pos=wx.Point(9,
              152), size=wx.Size(736, 507),
              style=wx.TE_AUTO_URL | wx.THICK_FRAME | wx.TE_LINEWRAP | wx.TE_READONLY | wx.TE_RICH2 | wx.VSCROLL | wx.TE_MULTILINE,
              value=u'')

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.FilePathDict = {}
        self.DependList = []
        self.selecteditem = ''
        RuleCheckerAPI.MISRACheckbox = self.checkBoxMISRA.GetValue()
        RuleCheckerAPI.Hi_intCheckbox = self.checkBoxHi_int.GetValue()
        RuleCheckerAPI.RICARDOCheckbox = self.checkBoxRICARDO.GetValue()
        self.gaugeProg.Hide()
        #self.styledTextCtrl1.SetDefaultStyle(wx.TextAttr("black","white",
        #         wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Times New Roman')))


    def flatten(self, lst):	
        return sum( ([x] if not isinstance(x, list) else self.flatten(x) for x in lst), [] ) 

    def OnButtonCancelButton(self, event):
        RuleCheckerAPI.CancelRuleCheck = True

    def OnBottonRuleCheckButton(self, event):
        self.styledTextCtrl1.Clear()
        RuleCheckerAPI.CancelRuleCheck = False
        if self.selecteditem != '':
            thread.start_new_thread(RuleCheckerAPI.RuleCheck, (self, self.DependList, self.FilePathDict, self.selecteditem))
            #RuleCheckerAPI.RuleCheck(self, self.DependList, self.FilePathDict, self.selecteditem)
        else:
            self.dispMsgBox("Please select a module from the List", "Information")

    def OnButtonFolderButton(self, event):
        self.listbox.Clear()
        self.selecteditem = ''
        self.treecntrl.DeleteAllItems()
        dialog = wx.DirDialog(None, "Choose a directory:",
                              defaultPath = os.getcwd(),
                              style=wx.DD_DEFAULT_STYLE | wx.DD_CHANGE_DIR)
        if dialog.ShowModal() == wx.ID_OK:
            dirname=dialog.GetPath()
            self.textCtrlFolder.Clear()
            self.textCtrlFolder.write(dirname)
        dialog.Destroy
        self.__searchFilesAndUpdateList()
        self.__checkDuplicatesInList()


    def OnTextCtrlFolderKillFocus(self, event):
        self.listbox.Clear()
        self.selecteditem = ''
        self.treecntrl.DeleteAllItems()
        self.__searchFilesAndUpdateList()
        self.__checkDuplicatesInList()

    def __searchFilesAndUpdateList(self):
        self.FilePathDict = {}
        for root, dirs, files in os.walk(self.textCtrlFolder.Value):
          for file in files:
            if file.endswith('.mdl'):
              #cfilespath.append(os.path.join(root, file))
              file = file.lower()
              self.FilePathDict[str(file[:-4])] = str(os.path.join(root, file))
              self.listbox.Append(file[:-4])

    def __checkDuplicatesInList(self):
        templist = []
        for index in range(self.listbox.GetCount()):
            templist.append(self.listbox.GetString(index))
        templistlen = len(templist)
        tempsetlen = len(list(set(templist)))
        if templistlen != tempsetlen:
            self.dispMsgBox("Selected folder has duplicate mdl files, Please select the folder having unique files", "Error")
            self.listbox.Clear()

    def OnListboxListbox(self, event):
        self.DependList = []
        sel = self.listbox.GetStringSelection()
        self.treecntrl.DeleteAllItems()
        root = self.treecntrl.AddRoot(sel)
        self.__checkDependency(sel)
        tDependList = []
        #Remove models without files.
        for checkDepItem in self.DependList:
            if checkDepItem in self.FilePathDict.keys():
                tDependList.append(checkDepItem)
        self.DependList = list(set(tDependList))
        DependListnew = list(set(self.DependList))
        DependListorg = list(set(self.DependList))

        for checkDepItem1 in DependListnew:
            self.DependList = []
            #branch = self.treecntrl.AddRoot(checkDepItem1)
            self.__checkDependency(checkDepItem1)
            tDependList = []
            #Remove models without files.
            for checkDepItem in self.DependList:
                if checkDepItem in self.FilePathDict.keys():
                    tDependList.append(checkDepItem)
            self.DependList = list(set(tDependList))
            self.DependList.append(checkDepItem1)
            DependListorg[DependListorg.index(checkDepItem1)] = self.DependList
            #self.__addTreeNodes(branch, list(set(self.DependList)))

        DependListorg = self.flatten(DependListorg)
        self.__addTreeNodes(root, list(set(DependListorg)))
        self.DependList = list(set(DependListorg))
        self.DependList.append(sel)
        self.treecntrl.Expand(root)
        self.selecteditem = sel

    def __addTreeNodes(self, parentItem, items):
        for item in items:
            if type(item) == str:
                self.treecntrl.AppendItem(parentItem, item)
            else:
                newItem = self.treecntrl.AppendItem(parentItem, item[0])
                self.__addTreeNodes(newItem, item[0])

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
                    checkDepLc = list(set([x.lower() for x in checkDep]))
                    try:
                        checkDepLc.remove(selection.lower())
                    except ValueError:
                        pass
                    self.DependList += checkDepLc
                if "SourceBlock" in fline:
                    checkDep = (re.split('[/]', fline.split('"')[1]))
                    if len(checkDep) == 2:
                        if checkDep[-1] not in ['Model Info', 'DocBlock', 'Function-Call\\nGenerator']:
                            self.DependList.append(checkDep[0].lower())
                            checkDepLc.append(checkDep[0].lower())
                            
            fileinput.close()
            for selx in checkDepLc:    # recursive
                self.__checkDependency(selx)
            #print checkDepLc

    def dispMsgBox(self, Message, ErrorType):
        dlg = wx.MessageDialog( self, Message, ErrorType, wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnCheckBoxMISRACheckbox(self, event):
        RuleCheckerAPI.MISRACheckbox = self.checkBoxMISRA.GetValue()

    def OnCheckBoxHi_intCheckbox(self, event):
        RuleCheckerAPI.Hi_intCheckbox = self.checkBoxHi_int.GetValue()

    def OnCheckBoxRICARDOCheckbox(self, event):
        RuleCheckerAPI.RICARDOCheckbox = self.checkBoxRICARDO.GetValue()

    def OnButtonQuitButton(self, event):
        self.Close()



class BoaApp(wx.App):
    def OnInit(self):
        self.main = create(None)
        self.main.Show()
        self.SetTopWindow(self.main)
        return True


if __name__ == '__main__':
    application = BoaApp(0)
    application.MainLoop()
