#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  6 10:26:55 2020

@author: BME, Moonspic
"""
from pathlib import Path
import  os, io, parse, json 

class CodeGen(object):
    def __init__(self):
        self.quote = '"'
        self.Spacing ="    "
        self.GeneralVariables_Marker = ["$V$","$V!"]
        self.ForVariables_Marker = ["$F$","$F!"]
        self.Variables_Marker = [self.GeneralVariables_Marker,self.ForVariables_Marker]
        self.CodeLineArray_Gen= "CodeLineArray_Gen"
        self.MarkerStart_ST = '$$Opt'
        self.MarkerStart_ET = '$!Opt'
        self.MarkerEnd = '$$End'
        self.MarkerFormat ='$$Opt.{}.{}.$!Opt'
        self.DefaultOptionMarkerAll= '$$Opt.{}.{}.Def.$!Opt'
        self.DefaultOptionMarker= '{}.Def'
        self.ForMarkerStart_ST = '$$For'
        self.ForMarkerStart_ET= '$!For'
        self.ForMarkerEnd = '$$EndFor'
        self.ForMarkerFormat = '$$For.{}.{}.$!For'
        self.ConfigMarkerStart_ST = '$$Config'
        self.ConfigMarkerStart_ET= '$!Config'
        self.ConfigMarkerEnd = '$$EndConfig'
        self.ConfigMarkerFormat = '$$config.{}.$!config'       
        self.ConfigFuncVariable  = 'configList'
        self.MarkerStart_ST = '$$Opt'
        self.MarkersListBegin =[[self.MarkerStart_ST,self.MarkerStart_ET],
                                [self.ForMarkerStart_ST,self.ForMarkerStart_ET]]
        self.MarkersListEnd=[self.MarkerEnd,self.ForMarkerEnd]
        self.MainFuncMarker=['#$$Func\n', '#$!Func\n']
        self.CommenterFuncMarker=['#$$ComFunc\n', '#$!ComFunc\n']
        self.DummyCommenterMarker=['#$$DumComFunc\n','#$!DumComFunc\n']
        self.FuncOptionsMarker = ['#$$Options\n','#$!Options\n']
        self.FuncOptionsDefaultMarker=['#$$DefOptions\n','#$!DefOptions\n']
        self.FuncAllParamsMarker=['#$$FuncAllParams\n','#$!FuncAllParams\n']
        self.DummayActiveParamMarker=['#$$DummyActiveParams\n','#$!DummyActiveParams\n']
        self.ImportStatMarker=['#$$ImportStat\n',"#$!ImportStat\n"]
        self.ForStatementMarker=["#$$For.VarListName.$!","#$$EndFor"]
        self.ConfigMarker=["#$$Config.KeyName.$!","#$$.EndConfig"]
        self.FunctionCommenter = "_Commenter"
        self.FunctionDummyCommenter = "_DummyCommenter"
        self.DefaultVariablesPattern = "_{}_"
        self.GenFun=True
        self.GenComFunc=True
        self.GenDumComFun=True
        self.GenOptions=True
        self.GenDefOptions=True
        self.GenAllParams=True
        self.DummyActive=True
        self.ImportStat=True
        self.CommentLineInsteadOfBlock=True
        self.DefinitionFuc =  "def {}({} {}): \n"
        self.ClassDefFunc = "class {}(object): \n"
        self.ClassFuncSign = 'self,'
        self.ClassFuncCall =  'self.'
        self.GeneralFuncSign= ""
        self.LineCommentSign='"#"'
        self.CommentDetector = "#"
        self.BlockCommentSign=["'3quote'","'3quote'"]
        self.IFStat= 'if {} == "{}":'
        self.ELIFStat = 'elif {} == "{}":'
        self.ForStat= 'for {} in {} :'
        self.ConfigStat= 'if {} in {}:' 
        self.AccessDict = '{}['"'{}'"']'
        self.LangParser = {
            self.MarkerStart_ST:{'Parser1': self.DefaultOptionMarkerAll,
                                 'Parser2':self.MarkerFormat,
                                 'StateModel1': {'Model':self.IFStat,"Spacing":0},
                                 'StateModel2':{'Model':self.ELIFStat,"Spacing":-1}},
            self.ForMarkerStart_ST:{'Parser1':self.ForMarkerFormat,
                                    'StateModel1':{'Model':self.ForStat,"Spacing":0}
                    }
            }
        self.CodeLines = []
        self.Params= {}#{opt1: ['a','b','c']}
        self.ParamsType ={}#{Opt1:"Option",Opt2:List"}
        self.ParamsDefault= {}#{opt1:'a'}
        self.Vars=set()
        self.MainFunction_Process=True
        self.Commenter_Process=True
        self.DummyCommenter_Process=True
        self.ProcessOptions=True
        self.writerFileName = "CodeWriter"
        
    def GetCommentsLines(self,codelines, commentDetector=None):
        if commentDetector==None:
            commentDetector = self.CommentDetector
        Result = []
        index = -1
        for line in codelines:
            index += 1 
            if line.strip()[0] == commentDetector:
                Result.append(index)
        return Result 
    def ClearParams(self):
        self.CodeLines=[]
        self.Params = {}
        self.ParamsDefault = {}
        self.Vars=set()
    def GetCurrentCodeParameters(self):
        Result = {}
        Result['CodeLine'] = self.CodeLines.copy()
        Result['Params'] = self.Params.copy()
        Result['ParamsDefault']  = self.ParamsDefault.copy()
        Result['ParamsType']  = self.ParamsType.copy()
        return Result 
    def StoreParams(self, Param,Option, DefaultParam=False,Type="Option"):        
        if not Param in self.ParamsType.keys():
            self.ParamsType[Param]=Type
        else:
            self.ParamsType[Param]=Type
        if Type=="List":
            self.Vars.add(Param)
            print(self.ParamsType)
        else:
            if not Param in self.Params.keys():
                self.Params[Param]= set()
            self.Params[Param].add(Option)
            if DefaultParam:
                if not Param in self.ParamsDefault:
                    self.ParamsDefault[Param]=''
                self.ParamsDefault[Param]=Option
    def GetLevelOfStatmentRelvance(self, param):
         Result = 1
         if param in self.Params.keys() and  param in self.ParamsType.keys():
             if self.ParamsType[param]=='Option':
                 Result = 2
         return Result
    def Get_NumOfSpacing(line):
        firstChar = line.strip()
        result = line.find(firstChar)
        return result 
    def ExtractSegment(self, line,MarkerStart_ST,MarkerStart_ET ):
        start = line.find(MarkerStart_ST)
        end = line.find(MarkerStart_ET)+len(MarkerStart_ET)
        segment = line[start:end]
        return segment
    def ReplaceWithEvalVar_Singleline(self, line,DictName , marker=[],quote = '"' ,config={}): 
        if config=={}:
            AccessDict = self.AccessDict
        else:
            AccessDict = config['AccessDict']
        if quote=="":
            quote = self.quote
        if marker== []:
            marker = self.Variables_Marker
        if marker[0] in line and marker[1] in line:
            start = line.find(marker[0])
            end = line.find(marker[1])
            start_len = len(marker[0])
            end_len = len(marker[1])        
            kval = line[start+start_len:end]
            codeWord = AccessDict.format(DictName,kval)
            orgWord = line[start:end+end_len]
            line = line.replace(orgWord,codeWord)
            line = self.ReplaceWithEvalVar_Singleline(line,DictName=DictName,marker=marker,quote= quote, config=config)
        
        Result = line
        return Result
    def GetFileLines(self,filePath, removeBlankLines=True ):
        File = Path(filePath)
        f = io.open(str(File.absolute()),'r')
        LinesArray = []
        for line in f:
            if removeBlankLines:
                if line.strip() != '':
                    LinesArray.append(line)
            else:
                LinesArray.append(line)
        return LinesArray
    def ExtractCodeSegment(self, codelines, BeginingMarker, EndMarker,MultipleSegment=False,FuncNameToMark="",FuncNameMarker="$!"):
        Result = []
        AppendInlist = False
        for line in codelines:
            if line.find(BeginingMarker)>-1:
                AppendInlist = True
                line = line[:-2]+ FuncNameMarker+FuncNameToMark+"\n"
            if line.find(EndMarker)>-1:
                line = line[:-2]+ FuncNameMarker+FuncNameToMark+"\n"
                Result.append(line)
                AppendInlist = False
                if MultipleSegment==False:
                    break
            if AppendInlist:
                Result.append(line)
        return Result 
    def SetTOList(self,setType):
        List= [x for x in setType]
        return List
    def SetTOList_Dict(self, DictWithSets):
        Result = {}
        for k,v in DictWithSets.items():
            try:
                List = [x for x in v]
                Result[k]=List
            except:
                Result[k]=v
        return Result
    def ProcessVar_Singleline(self, line, marker=[], returnStyle="Text",quote = '"', ApplyQuote=True, RegisterVariables =True ):
        if ApplyQuote:
            if quote=="":
                quote = self.quote
        else:
            quote =''
        if marker== []:
            marker = self.Variables_Marker
        L = line
        Vars = set()
        if marker[0] in line and marker[1] in line:
            start = line.find(marker[0])
            end = line.find(marker[1])
            start_len = len(marker[0])
            end_len = len(marker[1])        
            kval = line[start+start_len:end]
            kval = kval.strip()
            Vars.add(kval)        
            previousTxt = line[0:start]
            remainedText = line[end+end_len:]        
            ProcessRest = self.ProcessVar_Singleline(remainedText,marker, returnStyle="Dict" ,quote= quote)        
            remainedText_processed = ProcessRest["Text"]
            v = ProcessRest["Vars"]
            Vars = Vars.union(v)
            if remainedText != remainedText_processed :
                remainedText = remainedText_processed[1:-1] marks            
            L = quote + previousTxt + quote + " + " + kval + " + "  + quote + remainedText + quote   
        else:
            L =  quote +line+ quote
        if returnStyle=="Text":
            Result = L 
        elif returnStyle=="Dict":
            Result =  {"Text": L, "Vars":Vars}
        elif returnStyle == "Vars":
            Result = Vars   
        if RegisterVariables:
            for v in Vars:
                self.Vars.add(v)
        return Result  
    def ProcessVar_File(self, Init_codeLine, marker=[], quote = '', config={}): 
        if marker == []:
            marker = self.Variables_Marker
        if quote == '':
            quote = self.quote
        CodeLines=[]
        FuncVarialbes =set()
        for line in Init_codeLine:
            ProcessLine = self.ProcessVar_Singleline(line,marker=marker[0],returnStyle='Dict', quote=quote,ApplyQuote=False )
            FuncVarialbes.update(FuncVarialbes.union(ProcessLine['Vars']))
            line = ProcessLine['Text']
            ProcessLine = self.ProcessVar_Singleline(line,marker=marker[1],returnStyle='Dict', quote=quote)               
            line = ProcessLine['Text'].replace("\n","\\n")     
            CodeLines.append(line)
        Result ={'Vars':FuncVarialbes, 'CodeLines':CodeLines}
        return Result
    def GenInstruction(self, CodeList, GenType="Array",  config={"CodeLineArray_Gen":"CodeLineArray_Gen"}):
        ResutlCode  = []
        if GenType == "Array":
            if config=={}:
                CodeLineArray_Gen = self.CodeLineArray_Gen
            else:
                CodeLineArray_Gen = config['CodeLineArray_Gen']
            ResutlCode.append(CodeLineArray_Gen +" =[] ")
            WC = CodeLineArray_Gen + ".append({})"
        elif GenType =="Write":
            WC = 'f.write({})'          
        for line in CodeList:
            commandline =  WC.format(line)
            ResutlCode.append(commandline)       
        return ResutlCode
    def RegisterCodeLine(self,codeline):
        self.CodeLines.append(codeline)
    def RegistrationParamsLogic(self, MarkerFormat, Params):
        if MarkerFormat == self.MarkerFormat:
            self.StoreParams(Param = Params[0],Option=Params[1], DefaultParam=False,Type="Option" )
        elif MarkerFormat == self.DefaultOptionMarkerAll:
            self.StoreParams(Param = Params[0],Option=Params[1], DefaultParam=True,Type="Option" )
        elif MarkerFormat == self.ForMarkerFormat:
            self.StoreParams(Param = Params[1],Option=['#'], DefaultParam=False, Type="List")
    def PraseCodeLine(self, codeline,  Marker,currentSpacing, LevelOfStatmentRelvance=1,config={},SpacingSystem='    ', RegisterParams=False):
        codeline = codeline.strip()
        if config=={}:
            LangParser= self.LangParser         
        Model = LangParser[Marker]
        StatementModel = ''
        StatementKey = "StateModel" + str(LevelOfStatmentRelvance)
        StatementModel = Model[StatementKey]['Model']
        ValidParser = None
        Result = []
        ParserList = [x for x in Model.keys() if 'Parser' in x ]
        for x in ParserList:
            m = Model[x]
            Result = parse.parse(m, codeline)
            if Result!=None:
                ValidParser=Model[x] 
                break
        Spacing = Model[StatementKey]['Spacing']
        if Spacing < 0:
            for i in range(abs(Spacing)):
                currentSpacing = currentSpacing[len(SpacingSystem):]
        elif Spacing > 0:
            for i in range(Spacing):
                currentSpacing = currentSpacing + SpacingSystem
        Codeline = codeline
        if Result != None:
            Codeline = StatementModel.format(*Result)
            Result = [x for x in Result]
            if RegisterParams:                
                self.RegistrationParamsLogic(ValidParser, Result)
        else:
            Result =[]
        
        return Codeline, Result, currentSpacing
    def ProcessCodeLines(self, codelines, config={}): 
        self.ClearParams()
        Spacing = "    "        
        currentSpacing = ""
        Mark_beg =self.MarkersListBegin
        Mark_end =self.MarkersListEnd
        BeginMarkFlag=False
        EndMarkFlag=False
        index= -1
        for line in codelines:
            index += 1
            BeginMarkFlag=False
            EndMarkFlag=False
            Marker=""
            Maker_End=""
            for Mark in Mark_beg:
                Marker= ""
                if Mark[0] in line and Mark[1] in line:
                    BeginMarkFlag=True
                    Marker = Mark[0]
                    Maker_End = Mark[1]
                    break
            for mark_end in Mark_end:
                if mark_end in line:
                    EndMarkFlag= True
                    break
            if  EndMarkFlag:
                currentSpacing = currentSpacing[len(Spacing):]
                codelines[index]= currentSpacing + '\n'
            elif BeginMarkFlag:
                line = self.ExtractSegment(line,Marker,Maker_End)
                statement, params, _  = self.PraseCodeLine(codeline = line, Marker=Marker, currentSpacing=currentSpacing,SpacingSystem=Spacing,RegisterParams=False)
                if len(params)>0:
                    level= self.GetLevelOfStatmentRelvance(params[0])    
                    statement,params, cSpacing = self.PraseCodeLine(codeline = line, LevelOfStatmentRelvance=level, Marker=Marker, currentSpacing=currentSpacing,SpacingSystem=Spacing,RegisterParams=True) 
                    currentSpacing = cSpacing
                    codelines[index]= currentSpacing + statement
                    currentSpacing = currentSpacing+Spacing
            else:
                codelines[index]= currentSpacing + line                
            Codeline = codelines[index]

            self.RegisterCodeLine(Codeline)
        Results = self.GetCurrentCodeParameters()
        return Results 
    def Generate_FuncFile(self, WritingfilePath, funcName, CodeList, Variables, Options, DefalutOptions, 
                          ClassFunction=True,  GenCtrlConfig={}, LangConfig={}, MarkerConfig={}):
        if GenCtrlConfig=={}:
            GenFun =self.GenFun
            GenComFunc =self.GenComFunc
            GenDumComFun =self.GenDumComFun
            GenOptions =self.GenOptions
            GenDefOptions =self.GenDefOptions   
            GenAllParams = self.GenAllParams
            DummyActive=self.DummyActive
            ImportStat=self.ImportStat
        else:
            GenFun =GenCtrlConfig['GenFun']
            GenComFunc =GenCtrlConfig['GenComFunc']
            GenDumComFun =GenCtrlConfig['GenDumComFun']
            GenOptions =GenCtrlConfig['GenOptions']
            GenDefOptions =GenCtrlConfig['GenDefOptions']   
            selfStatment=GenCtrlConfig['CommentLineInsteadOfBlock'] 
            GenAllParams=['GenAllParams']
        if LangConfig =={}:
            DefinitionFuc = self.DefinitionFuc
            quote = self.quote
            spacing = self.Spacing
            codelistname = self.CodeLineArray_Gen
            LineCommentSign= self.LineCommentSign
            BlockCommentSign= self.BlockCommentSign
            DefaultVariablesPattern=self.DefaultVariablesPattern
            ClassFuncSign = self.ClassFuncSign 
            ClassFuncCall = self.ClassFuncCall 
        else:    
            DefinitionFuc= LangConfig['DefinitionFuc']
            quote = LangConfig['quote']
            spacing  = LangConfig['spacing']
            codelistname  = LangConfig['codelistname']
            LineCommentSign  = LangConfig['LineCommentSign']
            BlockCommentSign = LangConfig['BlockCommentSign']   
            DefaultVariablesPattern=LangConfig['DefaultVariablesPattern']
            ClassFuncSign = LangConfig['ClassFuncSign']
            ClassFuncCall = LangConfig['ClassFuncCall']
        if MarkerConfig=={}:
            MainFuncMarker= self.MainFuncMarker
            CommenterFuncMarker =self.CommenterFuncMarker
            DummyCommenterMarker= self.DummyCommenterMarker
            FuncOptionsMarker= self.FuncOptionsMarker
            FuncOptionsDefaultMarker= self.FuncOptionsDefaultMarker
            FuncAllParamsMarker=self.FuncAllParamsMarker
            FunctionCommenter = self.FunctionCommenter
            FunctionDummyCommenter =self.FunctionDummyCommenter
            DummayActiveParamMarker= self.DummayActiveParamMarker
            ImportStatMarker=self.ImportStatMarker
        else:      
            MainFuncMarker= MarkerConfig['MainFuncMarker']
            CommenterFuncMarker = MarkerConfig['CommenterFuncMarker']
            DummyCommenterMarker= MarkerConfig['DummyCommenterMarker']
            FuncOptionsMarker= MarkerConfig['FuncOptionsMarker']
            FuncOptionsDefaultMarker= MarkerConfig['FuncOptionsDefaultMarker']
            FuncAllParamsMarker=MarkerConfig['FuncAllParamsMarker']
            FunctionCommenter = MarkerConfig['FunctionCommenter']
            FunctionDummyCommenter =MarkerConfig['FunctionDummyCommenter']
            DummayActiveParamMarker= MarkerConfig['DummayActiveParamMarker']
            ImportStatMarker=MarkerConfig['ImportStatMarker']
        if ClassFunction:
            selfStatment = ClassFuncSign
            callSelfStatment = ClassFuncCall
        else:
            ClassFuncCall = self.GeneralFuncSign
            callSelfStatment =self.GeneralFuncSign
        if GenAllParams or GenDumComFun:
            if type(Variables)==dict:
                valid = True
                for k,v in Variables.items():
                    if type(v)!=list:
                        valid=False
                        break
                if valid:
                    Vars=Variables.copy()
            elif type (Variables)==set or type(Variables)==list:
                Vars ={}
                for x in Variables:
                    DymmyName = DefaultVariablesPattern.format(x) 
                    if x in self.ParamsType.keys():
                        if self.ParamsType[x]=='List':
                            DymmyName= "#"
                    Vars[x]= [DymmyName]
            AllParams = {**Vars, **Options}
            print("Vars")
            print(Vars)
            print("AllParams")
            print(AllParams)
        if GenDumComFun:
            DummyParams = {x:AllParams[x][0] for x in AllParams.keys()}
            for k,v in DefalutOptions.items():
                for kDum in DummyParams.keys():
                    if kDum==k:
                        DummyParams[kDum]=v       
        File = Path(WritingfilePath)
        f = io.open(str(File.absolute()), 'w+')    
        if type(Variables)==set:
            Variables = [x for x in Variables]
        params = ''
        if len(Variables)>0:
            params = Variables[0]
            for x in range(1,len(Variables)):
                    params = params + ',' + Variables[x]
        if len(Options)>0:
            if params != "" :
                for o in Options:
                    if o in DefalutOptions.keys():
                        if DefalutOptions[o] != '':
                            o = o + ' = ' + quote + DefalutOptions[o] + quote
                        params = params + ',' + o 
            else:
                print("Options")
                print(Options)
                params = Options[0]
                for o in range(1,len(Options)):
                        params = params + ',' + Options[x]
        if ImportStat:
            f.write(ImportStatMarker[0])
            f.write("import itertools \n")
            f.write(ImportStatMarker[1])
            f.write("\n")
        if GenFun:
            f.write(MainFuncMarker[0])
            FuncDef = DefinitionFuc.format(funcName,selfStatment,params)        
            f.write(FuncDef)        
            for line in CodeList:
                f.write(spacing+ line + "\n")    
            f.write(spacing+"return {}".format(codelistname)+"\n")
            f.write(MainFuncMarker[1])
            f.write("\n") 
        if  GenComFunc: 
            f.write(CommenterFuncMarker[0])
            configStatment ="'blockComment':{'start': "+BlockCommentSign[0]+",'end': "+BlockCommentSign[1]+"},'lineComment':"+LineCommentSign
            CommentParams = "ParamsOptions, ActiveParams, BlockComment=False, Config={"+configStatment+"}"
            CommenterFuncName = funcName+FunctionCommenter
            FuncDef = DefinitionFuc.format(CommenterFuncName,selfStatment,CommentParams)
            f.write(FuncDef)
            f.write(spacing +"blockComment_S= Config['blockComment']['start'] \n")
            f.write(spacing +"blockComment_E= Config['blockComment']['end']\n")
            f.write(spacing + "lineComment=Config['lineComment'] \n")
            f.write(spacing + "paramlist = [v for v in ParamsOptions.values()]\n")
            f.write(spacing + "paramskeys = [k for k in ParamsOptions.keys()]\n")
            f.write(spacing + "AllCombinations = list(itertools.product(*paramlist))\n")
            f.write(spacing + "paramsCombinations =[dict(zip(paramskeys,c)) for c in AllCombinations]\n")
            f.write(spacing + "GenCodeList =[]\n")
            f.write(spacing + "Comment = lineComment +' Active Code \\n' \n")
            f.write(spacing + "GenCodeList.append(Comment) \n")
            f.write(spacing + "ActiveOutput =  {}{}(**ActiveParams)\n".format(callSelfStatment,funcName))
            f.write(spacing + "GenCodeList.extend(ActiveOutput)\n")
            f.write(spacing + "for i in range(len(paramsCombinations)): \n" )
            f.write(spacing + spacing + "comment = '# GenCase {}'.format(i) \n")
            f.write(spacing + spacing + "params = paramsCombinations[i]\n")
            f.write(spacing + spacing + "GenCodeList.append(comment)\n")
            f.write(spacing + spacing + "codelist =  {}{}(**params)\n".format(callSelfStatment,funcName))
            f.write(spacing + spacing + "if BlockComment:\n")
            f.write(spacing + spacing + spacing +"GenCodeList.append(blockComment_S + ' \\n') \n" )
            f.write(spacing + spacing + spacing + "GenCodeList.extend(codelist)\n" )
            f.write(spacing + spacing + spacing + "GenCodeList.append(blockComment_E + '\\n') \n")
            f.write(spacing + spacing +  "else: \n")
            f.write(spacing + spacing + spacing + "codelist_Comm = [lineComment+'{}'.format(x) for x in codelist] \n")
            f.write(spacing + spacing + spacing + "GenCodeList.extend(codelist_Comm) \n")
            f.write(spacing + "return GenCodeList \n")
            f.write(CommenterFuncMarker[1])
            f.write("\n")
            f.write("\n")
        if GenDumComFun:
            f.write(DummyCommenterMarker[0])
            CommentParams = "Config={}"
            DummyCommenterFuncName = funcName + FunctionDummyCommenter
            FuncDef = DefinitionFuc.format(DummyCommenterFuncName,selfStatment,CommentParams)
            f.write(FuncDef + "\n")
            dummypParms = json.dumps(DummyParams)
            DummyParamsStatment = "ActiveParams = " + dummypParms
            f.write(spacing + DummyParamsStatment + "\n")
            allParamsStr = json.dumps(AllParams)
            allParamasStat = "ParamsOptions = " + allParamsStr 
            f.write(spacing + allParamasStat + "\n")
            callStatment = "CodeList = self.{}(ParamsOptions,ActiveParams)\n".format(CommenterFuncName)
            f.write(spacing +  callStatment)
            f.write(spacing +  "return CodeList\n")
            f.write(DummyCommenterMarker[1])
        if GenOptions:
            f.write("\n")
            f.write("\n")
            f.write("\n")
            f.write(FuncOptionsMarker[0])
            optString = json.dumps(Options)
            Options_String = funcName + '_Options = ' + optString
            f.write(Options_String + "\n")
            f.write(FuncOptionsMarker[1])
        if GenDefOptions:
            f.write("\n")
            f.write(FuncOptionsDefaultMarker[0])
            optDefString = json.dumps(DefalutOptions)
            OptionsDef_String = funcName + '_Default_Options = ' + optDefString
            f.write(OptionsDef_String + "\n")
            f.write(FuncOptionsDefaultMarker[1])
            f.write("\n")
        if GenAllParams or GenDumComFun :
            f.write("\n")
            f.write(FuncAllParamsMarker[0])
            allParamsString = json.dumps(AllParams)
            AllParams_String = funcName + '_AllParams = ' + allParamsString
            f.write(AllParams_String + "\n")            
            f.write(FuncAllParamsMarker[1])
        if DummyActive or GenDumComFun :
            f.write("\n")
            f.write(DummayActiveParamMarker[0])
            DummyParamsString = json.dumps(DummyParams)
            DummyParams_Statment = funcName + 'DummyActiveParams = ' + DummyParamsString
            f.write(DummyParams_Statment + "\n")            
            f.write(DummayActiveParamMarker[1])
        f.close()     
    def CompleCodeFileProcessing_WriterGen(self, inputFilePath,outputFilePath,OutputFuncName, ClassFuncSign=True):
        lineCode =self.GetFileLines(inputFilePath)
        codeProcessedVar = self.ProcessVar_File(lineCode)
        Varcode = codeProcessedVar['CodeLines']
        variables = self.Vars.copy()
        print("variables")
        print(variables)
        CodeInst = self.GenInstruction(Varcode,GenType="Array")
        ProcessedCode = self.ProcessCodeLines(CodeInst)
        codelist = ProcessedCode['CodeLine']
        options =ProcessedCode['Params']
        defOptions = ProcessedCode['ParamsDefault']
        options = self.SetTOList_Dict(options) self.Generate_FuncFile(outputFilePath,OutputFuncName,codelist,variables,options,defOptions,ClassFuncSign)
    def ProcessDirectory(self, DirectorPath, ClassFuncSign=True):
        p = Path(DirectorPath)
        OutputSuffix = "_CodeWriter"
        Extension = ".py"
        OutputDirName = p.name+OutputSuffix
        NewDir = p.parent.as_posix()+'/{}/'.format(OutputDirName)
        os.mkdir(NewDir)
        filesPathObj =  p.glob("*.py")
        listFiles = [x for x in filesPathObj]                
        for file in listFiles:
            filePath = file.as_posix()
            fileName = file.name
            extloc =  fileName.find(Extension)
            fileName = fileName[:extloc]
            newFileName = fileName+OutputSuffix+Extension
            newFilePath = OutputDirName+"/"+newFileName self.CompleCodeFileProcessing_WriterGen(filePath,newFilePath,fileName,ClassFuncSign)
    def CreateCodeWriter(self,DirectoryPath, ext=".py", config={}):
        if config=={}:
            MainFunction_Process=self.MainFunction_Process
            Commenter_Process=self.Commenter_Process
            DummyCommenter_Process=self.DummyCommenter_Process
            ProcessOptions= self.ProcessOptions
            writerFileName= self.writerFileName
            ClassDefFunc = self.ClassDefFunc
            MainFuncMarker= self.MainFuncMarker
            CommenterFuncMarker=self.CommenterFuncMarker
            DummyCommenterMarker= self.DummyCommenterMarker
            FuncOptionsMarker=self.FuncOptionsMarker
            Spacing = self.Spacing
        else:
            MainFunction_Process=config['MainFunction_Process']
            Commenter_Process=config['Commenter_Process']        
            DummyCommenter_Process=config['DummyCommenter_Process']
            ProcessOptions=config['ProcessOptions']
            writerFileName=config['writerFileName']
            ClassDefFunc=config['ClassDefFunc']
            
            MainFuncMarker=config['MainFuncMarker']
            CommenterFuncMarker=config['CommenterFuncMarker']
            DummyCommenterMarker=config['DummyCommenterMarker']
            FuncOptionsMarker=config['FuncOptionsMarker']
            Spacing=config['Spacing']
        p = Path(DirectoryPath)
        filesPathObj = p.glob("*{}".format(ext))
        listFiles = [x for x in filesPathObj]
        Writerfile = p.joinpath(writerFileName).as_posix()+ext
        OptionFileName = writerFileName+"_Options"
        OptionFile = p.joinpath(OptionFileName).as_posix()+ext
        f = io.open(Writerfile, 'w+')
        o = io.open(OptionFile,'w+')
        f.write("import itertools \n")
        f.write(ClassDefFunc.format(writerFileName))
        for file in listFiles:
            filepath = file.as_posix()
            filelines = self.GetFileLines(filepath)
            if MainFunction_Process:
                MainFuncCode = self.ExtractCodeSegment(filelines,MainFuncMarker[0],MainFuncMarker[1],False, file.name)
                for line in MainFuncCode:
                    f.write(Spacing + line)  
            f.write('\n')
            if Commenter_Process:
                CommenterCode = self.ExtractCodeSegment(filelines,CommenterFuncMarker[0],CommenterFuncMarker[1],False, file.name)
                for line in CommenterCode:
                    f.write(Spacing + line)
            f.write('\n')
            if DummyCommenter_Process:
                DummyCommenterCode = self.ExtractCodeSegment(filelines,DummyCommenterMarker[0],DummyCommenterMarker[1],False, file.name)
                for line in DummyCommenterCode:
                    f.write(Spacing + line)
            f.write('\n')
            if ProcessOptions:
                Options = self.ExtractCodeSegment(filelines,FuncOptionsMarker[0],FuncOptionsMarker[1],False, file.name)
                for line in Options:
                    o.write(Spacing + line)
            o.write('\n')
        f.close()
        o.close()