# -*- coding: utf-8 -*-

class Environment:
      
    #std    
    import sys
    import traceback    
    import unicodedata
    import os
    #clr    
    import clr
    clr.AddReference('System')
    clr.AddReference('System.IO')    
    clr.AddReference('PresentationCore')
    clr.AddReference("PresentationFramework")
    clr.AddReference("System.Windows")
    clr.AddReference("System.Xaml")
    clr.AddReference("WindowsBase")
    from System.Windows import MessageBox

    #
    @classmethod
    def AppData(cls): return cls.os.getenv('APPDATA')

    @classmethod
    def PrgData(cls): return cls.os.getenv('PROGRAMDATA')

    @classmethod
    def PrgFl64(cls): return cls.os.getenv('PROGRAMFILES')

    @classmethod
    def PrgFl32(cls): return cls.os.getenv('PROGRAMFILES(X86)')

    @classmethod
    def UserDir(cls): return cls.os.getenv('USERPROFILE')

    @classmethod
    def UserDoc(cls): return cls.os.path.join(cls.os.getenv('USERPROFILE'), "Documents")    

    @classmethod
    def JoinPath(cls, pathl, pathr): return cls.os.path.join(pathl, pathr)

    #
    @classmethod
    def Exit(cls): cls.sys.exit("Exit current environment!")

    @classmethod
    def GetLastError(cls):
        info = cls.sys.exc_info()
        infos = ''.join(cls.traceback.format_exception(info[0], info[1], info[2]))
        return infos

    @classmethod
    def Message(cls, msg):
        if not msg is None and type(msg) == str:
            cls.MessageBox.Show(msg)
        else:
            cls.MessageBox.Show("Empty argument or non string error message!")

    @classmethod
    def SafeCall(cls, code, tail, show):        
        back = None
        flag = 0
        info = "empty"
        if not code is None:
            try:            
                back = code(tail)
                flag = 1
            except:
                exc_t, exc_v, exc_i = sys.exc_info()           
                info = ''.join(cls.traceback.format_exception(exc_t, exc_v, exc_i))         
                if show: cls.Message(info)         
        return [flag, back, info]


pyliblocalpath = Environment.JoinPath(Environment.AppData(), 'pyRevit\extensions\lib')
pylibexceltemplocalpath = Environment.JoinPath(pyliblocalpath, '?????????????? ????????????????????.xlsx')
pylibexceldestlocalpath = Environment.JoinPath(Environment.UserDoc(), '?????????????? ????????????????????.xlsx')

import os.path as op
import os
import sys
import clr
import math
import collections
from shutil import copyfile
clr.AddReference('System')
clr.AddReference('System.IO')
clr.AddReference("System.Windows.Forms")
clr.AddReference("EPPlus")
from System.IO import FileInfo
from System.Windows.Forms import MessageBox, SaveFileDialog, DialogResult
from System.Collections.Generic import List 
from Autodesk.Revit.DB import FilteredElementCollector, ElementId, Wall, Floor, FootPrintRoof, BuiltInCategory, FamilyInstance
from Autodesk.Revit.Creation import ItemFactoryBase
from Autodesk.Revit.UI.Selection import PickBoxStyle 
from Autodesk.Revit.UI import RevitCommandId, PostableCommand
from OfficeOpenXml import ExcelPackage

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application
view = __revit__.ActiveUIDocument.ActiveGraphicalView 
view = doc.ActiveView


def FacadeCladding():
    walls = [x for x in FilteredElementCollector(doc).OfClass(Wall).ToElements() if '(??)' in x.Name]
    
    totalVolume = {}

    for wall in walls:
        compoundStructure = wall.WallType.GetCompoundStructure()

        if compoundStructure:
            for layer in compoundStructure.GetLayers():
                layerWidth = layer.Width*0.3048
                materialId = layer.MaterialId

                material = doc.GetElement(materialId)
                note = material.LookupParameter('??????????????????????')
                if note:
                    if note.AsString() == '?????????????????? ????????????':
                        name = material.Name[1:]
                        materialVolume = wall.GetMaterialVolume(materialId)*(0.3048**3)
                        if name in totalVolume:
                            totalVolume[name] += materialVolume/layerWidth
                        else:
                            totalVolume[name] = materialVolume/layerWidth
    return totalVolume


def InsulationCladding():
    elements = [x for x in FilteredElementCollector(doc).OfClass(Wall).ToElements()]
    elements += [x for x in FilteredElementCollector(doc).OfClass(Floor).ToElements()] 
    elements += [x for x in FilteredElementCollector(doc).OfClass(FootPrintRoof).ToElements()] 

    totalVolume = {}

    for element in elements:
        for materialId in element.GetMaterialIds(0):

            material = doc.GetElement(materialId)
            note = material.LookupParameter('??????????????????????')
            if note:
                if note.AsString() == '??????????????????????????':
                    name = material.Name[1:]
                    materialVolume = element.GetMaterialVolume(materialId)*(0.3048**3)
                    if name in totalVolume:
                        totalVolume[name] += materialVolume
                    else:
                        totalVolume[name] = materialVolume
    return totalVolume


def BrickworkCladding():
    elements = [x for x in FilteredElementCollector(doc).OfClass(Wall).ToElements()]
    elements += [x for x in FilteredElementCollector(doc).OfClass(Floor).ToElements()] 
    elements += [x for x in FilteredElementCollector(doc).OfClass(FootPrintRoof).ToElements()] 

    totalVolume = {}

    for element in elements:
        for materialId in element.GetMaterialIds(0):

            material = doc.GetElement(materialId)
            note = material.LookupParameter('??????????????????????')
            if note:
                if note.AsString() == '????????????':
                    name = material.Name[1:]
                    materialVolume = element.GetMaterialVolume(materialId)*(0.3048**3)
                    if name in totalVolume:
                        totalVolume[name] += materialVolume
                    else:
                        totalVolume[name] = materialVolume
    return totalVolume


def WindowsCount():
    elements = [x for x in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).ToElements()]

    totalCount = {}

    for element in elements:
        if isinstance(element, FamilyInstance):
            name = element.Name
            familyName = element.Symbol.FamilyName
            if "????-" in familyName:
                familyName = familyName[3:]
            name = '{}: {}'.format(familyName, name)
            if '??????????' in name.lower():
                continue
            if name in totalCount:
                totalCount[name] +=1
            else:
                totalCount[name] =1

    return totalCount


def DoorsCount():
    elements = [x for x in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).ToElements()]

    totalCount = {}

    for element in elements:
        if isinstance(element, FamilyInstance):
            name = element.Name
            familyName = element.Symbol.FamilyName
            if "????-" in familyName:
                familyName = familyName[3:]
            name = '{}: {}'.format(familyName, name)
            if '??????????' in name.lower():
                continue
            if name in totalCount:
                totalCount[name] +=1
            else:
                totalCount[name] =1

    return totalCount





baseFileName = pylibexceltemplocalpath #"W:\BIM-??????????\!????????????????????????????????\????????????????????????\?????????????????? ?? ?????????????? Excel\?????????????? ????????????????????.xlsx"
tableSheets = {
    '?????????????????? ????????????' : FacadeCladding,
    '????????????????????': InsulationCladding,
    '????????????': BrickworkCladding,
    '????????': WindowsCount,
    '??????????': DoorsCount
}

saveFileDialog = SaveFileDialog()
saveFileDialog.Filter = "xlsx files (*.xlsx)|*.xlsx|All files (*.*)|*.*"  
saveFileDialog.FilterIndex = 1 
saveFileDialog.RestoreDirectory = True 
 
if saveFileDialog.ShowDialog() == DialogResult.OK:
    
    fileName = saveFileDialog.FileName
    #Environment.Message(baseFileName)
    #Environment.Message(fileName)
    copyfile(baseFileName, fileName)

    existingFile = FileInfo(fileName)
    package = ExcelPackage(existingFile)
    worksheetsList = package.Workbook.Worksheets


    for worksheet in worksheetsList:
        worksheetName = worksheet.ToString()
        #print "---------------"
        #print worksheetName
        #print "---------------"
        if worksheetName in tableSheets:
            tableData = tableSheets[worksheetName]()
            for index, (key, value) in enumerate(sorted(tableData.items())):
                #print "{}.{}: {}".format(index, key, value)
                worksheet.Cells[4 + index, 2].Value = key
                worksheet.Cells[4 + index, 3].Value = value

    newFile = FileInfo(pylibexceldestlocalpath) #'W:\BIM - ??????????\!????????????????????????????????\????????????????????????\?????????????????? ?? ?????????????? Excel\?????????????? ????????????????????_2.xlsx')
    #package.SaveAs(FileInfo)
    package.Save()
    package.Dispose()

MessageBox.Show('????????????!')