

CCSettingsList = {'Simulink.SolverCC' :        # Solver
                             {
                                'StartTime' : '0.0',
                                'StopTime' : 'inf',
                                'SolverMode' : 'SingleTasking',
                                'Solver' : 'FixedStepDiscrete',
                                'SolverName' : 'FixedStepDiscrete',
#Defined by Solver and SolverName   'SolverType' : 'Fixed-Step',
                                'AutoInsertRateTranBlk' : 'off'
                             },
                  'Simulink.DataIOCC' :        # DataIO
                             {  'SaveFormat' : 'StructureWithTime'},
                  'Simulink.OptimizationCC' :  # Optimization
                             {
                                'BlockReduction' : 'off',
                                'BooleanDataType' : 'on',
                                'ConditionallyExecuteInputs' : 'off',
                                'UseSpecifiedMinMax' : 'off',
                                'ExpressionFolding' : 'off',
                                'RollThreshold' : 5,
                                'ZeroExternalMemoryAtStartup' : 'on',
                                'ZeroInternalMemoryAtStartup' : 'on',
                                'NoFixptDivByZeroProtection' : 'on',
                                'EfficientFloat2IntCast' : 'off',
                                'EfficientMapNaN2IntZero' : 'off',
                                'LifeSpan' : 'inf',
                                'InitFltsAndDblsToZero' : 'off'
                             },
                  'Simulink.DebuggingCC' :      #Diag_Signal_Data
                             {
                                'RTPrefix' : 'error',
                                'ArrayBoundsChecking' : 'none',
                                'SignalInfNanChecking' : 'error',
                                'SignalRangeChecking' : 'error',
                                'CheckMatrixSingularityMsg' : 'error',
                                'IntegerOverflowMsg' : 'error',
                                'UnderSpecifiedDataTypeMsg' : 'error',
                                'UniqueDataStoreMsg' : 'error',
                                                 #  'Diag_Data_Stores' : 
                                'ReadBeforeWriteMsg' : 'EnableAllAsError',
                                'WriteAfterWriteMsg' : 'EnableAllAsError',
                                'WriteAfterReadMsg' : 'EnableAllAsError',
                                'MultiTaskDSMMsg' : 'error',
                                                 #  'Diag_Solver' : 
                                'AlgebraicLoopMsg' : 'error',
                                'ArtificialAlgebraicLoopMsg' : 'error',
                                'BlockPriorityViolationMsg' : 'error',
                                'SolverPrmCheckMsg' : 'error',
                                'UnknownTsInhSupMsg' : 'error',
                                'StateNameClashWarn' : 'warning',
                                                 #  'Diag_Saving' : 
                                'SaveWithDisabledLinksMsg' : 'warning',
                                'SaveWithParameterizedLinksMsg' : 'warning',
                                                 #  'Diag_Init' : 
                                'CheckSSInitialOutputMsg' : 'on',
                                'CheckExecutionContextPreStartOutputMsg' : 'on',
                                'CheckExecutionContextRuntimeOutputMsg' : 'on',
                                                 #  'Diag' : 
                                'SignalResolutionControl' : 'UseLocalSettings',
                                                 #  'Diag_Sample_Time' : 
                                'InheritedTsInSrcMsg' : 'warning',
                                'DiscreteInheritContinuousMsg' : 'error',
                                'MultiTaskCondExecSysMsg' : 'error',
                                'MultiTaskRateTransMsg' : 'error',
                                'SingleTaskRateTransMsg' : 'error',
                                'TasksWithSamePriorityMsg' : 'error',
                                'SigSpecEnsureSampleTimeMsg' : 'error',
                                                 #  'Diag_Data_Type' : 
                                'Int32ToFloatConvMsg' : 'warning',
                                'UnnecessaryDatatypeConvMsg' : 'warning',
                                'VectorMatrixConversionMsg' : 'error',
                                                 #  'Diag_Parameter' : 
                                'ParameterDowncastMsg' : 'error',
                                'ParameterOverflowMsg' : 'error',
                                'ParameterUnderflowMsg' : 'error',
                                'ParameterPrecisionLossMsg' : 'warning',
                                'ParameterTunabilityLossMsg' : 'error',
                                                 #  'Diag_Function_Call' : 
                                'InvalidFcnCallConnMsg' : 'error',
                                'FcnCallInpInsideContextMsg' : 'Enable All',
                                                 #  'Diag_Sig_Connectivity' : 
                                'SignalLabelMismatchMsg' : 'warning',
                                'UnconnectedInputMsg' : 'error',
                                'UnconnectedOutputMsg' : 'error',
                                'UnconnectedLineMsg' : 'error',
                                                 #  'Diag_Compatibility' : 
                                'SFcnCompatibilityMsg' : 'error',
                                                 #  'Diag_Bus_Connectivity' : 
                                'BusObjectLabelMismatch' : 'error',
                                'RootOutportRequireBusObject' : 'error',
                                'StrictBusMsg' : 'ErrorOnBusTreatedAsVector',
                                                 #  'Diag_Debug' : 
                                'AssertControl' : 'DisableAll',
                                                 #  'Diag_Model_Referencing' : 
                                'ModelReferenceIOMsg' : 'error',
                                'ModelReferenceVersionMismatchMessage' : 'none',
                                'ModelReferenceIOMismatchMessage' : 'error',
                                'ModelReferenceCSMismatchMessage' : 'warning',
                                'ModelReferenceDataLoggingMessage' : 'error'
                             },
                  'Simulink.HardwareCC' :        #HW_Implementation
                             {
                                'ProdShiftRightIntArith' : 'on',
                                'ProdHWDeviceType' : 'Freescale->MPC82xx'								
                             },
                  'Simulink.ModelReferenceCC' :  #Model_Referencing
                             {
                                'UpdateModelReferenceTargets' : 'IfOutOfDate',
                                'ModelReferenceNumInstancesAllowed' : 'Single',
                                'ModelReferencePassRootInputsByReference' : 'on',
                                'ModelReferenceMinAlgLoopOccurrences' : 'off'
                             },
                  'Simulink.RTWCC' :             # RTW
                             {
                                'IncludeHyperlinkInReport' : 'on',
                                'GenerateTraceInfo' : 'on',
                                'GenerateTraceReport' : 'on',
                                'GenerateTraceReportSl' : 'on',
                                'GenerateTraceReportSf' : 'on',
                                'GenerateTraceReportEml' : 'on',
                                'ObjectivePriorities' : ['Traceability','Safety precaution'],
                                'CheckMdlBeforeBuild' : 'Warning'
                             },
                  'Simulink.CodeAppCC' :         # RTW_Code_Appearance
                             {
                                'ForceParamTrailComments' : 'on',
                                'GenerateComments' : 'on',
                                'MaxIdLength' : 31,
                                'ShowEliminatedStatement' : 'on',
                                'SimulinkDataObjDesc' : 'on',
                                'SFDataObjDesc' : 'on',
                                'MangleLength' : 4,
                                'CustomSymbolStrGlobalVar' : '$R$N$M',
                                'CustomSymbolStrType' : '$N$R$M',
                                'CustomSymbolStrField' : '$N$M',
                                'CustomSymbolStrFcn' : '$R$N$M$F',
                                'CustomSymbolStrFcnArg' : 'rt$I$N$M',
                                'CustomSymbolStrBlkIO' : 'rtb_$N$M',
                                'CustomSymbolStrTmpVar' : '$N$M',
                                'CustomSymbolStrMacro' : '$R$N$M_D',
                                'CustomCommentsFcn' : 'taxibot_comments_mptfun.m',
                                'DefineNamingRule' : 'None',
                                'ParamNamingRule' : 'None',
                                'SignalNamingRule' : 'None',
                                'InsertBlockDesc' : 'on',
                                'SimulinkBlockComments' : 'on',
                                'EnableCustomComments' : 'on',
                                'InlinedPrmAccess' : 'Literals',
                                'ReqsInCode' : 'on'
                             },
                  'Simulink.ERTTargetCC' :      # RTW_ERT_Target
                             {
                                'TargetFunctionLibrary' : 'C89/90 (ANSI)',
                                'ERTMultiwordLength' : 256,
                                'GenerateSampleERTMain' : 'off',
                                'IncludeMdlTerminateFcn' : 'off',
                                'GeneratePreprocessorConditionals' : 'Enable all',
                                'CombineOutputUpdateFcns' : 'on',
                                'SuppressErrorStatus' : 'on',
                                'SupportAbsoluteTime' : 'off',
                                'MatFileLogging' : 'off',
                                'SupportNonFinite' : 'off',
                                'SupportComplex' : 'off',
                                'SupportContinuousTime' : 'off',
                                'SupportNonInlinedSFcns' : 'off',
                                'SupportVariableSizeSignals' : 'off',
                                'ParenthesesLevel' : 'Maximum',
                                'PortableWordSizes' : 'off',
                                'GenerateASAP2' : 'on',
                                'InlinedParameterPlacement' : 'Hierarchical',
                                'ERTSrcFileBannerTemplate' : 'taxibot_code_c_template.cgt',
                                'ERTHdrFileBannerTemplate' : 'taxibot_code_h_template.cgt',
                                'ERTDataSrcFileTemplate' : 'taxibot_data_c_template.cgt',
                                'ERTDataHdrFileTemplate' : 'taxibot_data_h_template.cgt',
                                'GRTInterface' : 'off',
                                'PreserveExpressionOrder' : 'on',
                                'PreserveIfCondition' : 'on',
                                'ConvertIfToSwitch' : 'off',
                                'EnableUserReplacementTypes' : 'on',
                                'UtilityFuncGeneration' : 'Shared location'							
                             }}

DataStoreCC = {                # Checks Rule HISL_0013 A
                'HISL_0013 A': {'UniqueDataStoreMsg' : 'error',
                                'ReadBeforeWriteMsg' : 'EnableAllAsError',
                                'WriteAfterWriteMsg' : 'EnableAllAsError',
                                'WriteAfterReadMsg' : 'EnableAllAsError',
                                'MultiTaskDSMMsg' : 'error'},
                               # Checks Rule HISL_0005 C
                'HISL_0005 C': {'CheckMatrixSingularityMsg' : 'error'}
              }

AllowedOtherBlocks = {
                        'BusCreator'          : [],
                        'BusSelector'         : [],
                        'Concatenate'         : [],
                        'Mux'                 : [],
                        'Demux'               : [],
                        'From'                : [],
                        'Goto'                : [],
                        'GotoTagVisibility'   : [],
                        'Merge'               : [],
                        'Inport'              : [],
                        'Outport'             : [],
                        'Terminator'          : [],
                        'Constant'            : ['Value'],
                        'If'                  : [],
                        'SwitchCase'          : [],
                        'RateTransition'      : [],
                        'DataTypeConversion'  : [],
                        'Lookup'              : ['InputValues', 'Table'],
                        'Lookup2D'            : ['RowIndex', 'ColumnIndex', 'Table'],
                        'Chart'               : [],
                        'UnitDelay'           : ['X0'],
                        'DiscreteIntegrator'  : ['InitialCondition'],
                        'DiscreteTransferFcn' : ['Numerator', 'Denominator'],
                        'Sum'                 : [],
                        'Gain'                : ['Gain'],
                        'Product'             : [],
                        'Abs'                 : [],
                        'Math'                : [],
                        'MinMax'              : [],
                        'Trigonometry'        : [],
                        'Sqrt'                : [],
                        'Logic'               : [],
                        'RelationalOperator'  : [],
                        'Relay'               : ['OnSwitchValue', 'OffSwitchValue', 'OnOutputValue', 'OffOutputValue'],
                        'Saturate'            : ['UpperLimit', 'LowerLimit'],
                        'Switch'              : ['Threshold'],
                        'ActionPort'          : [],
                        'TriggerPort'         : [],
                        'MultiPortSwitch'     : [],
                        'Selector'            : []
                     }

AllowedSubsystemBlocks = {
                             'ActionType': ['then', 'else', 'case', 'default','elseif'],
                             'TreatAsAtomicUnit': ['on'],
                             'RTWSystemCode':  ['Auto', 'Reusable function', 'Function'],
                             'MaskType': ['CMBlock', 'Compare To Constant', 'DocBlock',
                                          'Conversion', 'ReqId','Stateflow']
                         }

AllowedModelReferenceBlocks = {
                                 'MaskType': ['Asymmetrical Debounce', 'Falling Edge', 'First order filter', 'Hysteresis',
                                              'Latch', 'Periodic enable', 'Rate Limiter', 'Rising edge',
                                              'Running average', 'SR Latch', 'Symmetrical Debounce']
                              }

AllowedReferenceBlocks = {
                            'SourceType' : ['Asymmetrical Debounce', 'CMBlock', 'Conversion',
                                            'DocBlock', 'Falling Edge', 'Hysteresis',
                                            'Latch', 'Lookup Table Dynamic', 'Rate Limiter',
                                            'ReqId', 'Rising edge', 'Saturation Dynamic',
                                            'SR Latch', 'SubSystem', 'Symmetrical Debounce'
                                            'Function-Call Generator', 'Compare To Constant',
                                            'First order filter','Periodic enable',
                                            'Running average','Symmetrical Debounce'],
                         }
                         
AttributesFormatString = {
                            'Lookup'              : '<input=%<inputvalues>>\\\\n<output=%<outputvalues>>',
                            'UnitDelay'           : '<initial=%<x0>>\\\\n<tsample=%<sampleTime>>',
                            'Switch'              : '<threshold=%<threshold>>\\\\n<criteria=%<Criteria>>',
                            'DiscreteIntegrator'  : '<initial=%<initialcondition>>\\\\n<tsample=%<sampleTime>>\\\\n<limits=%<UpperSaturationLimit>/%<LowerSaturationLimit>(%<LimitOutput>)>',
                            'DiscreteZeroPole'    : '<tsample=%<sampleTime>>\\\\n<gain=%<gain>>',
                            'Outport'             : '<tsample=%<SampleTime>>',
                            'Inport'              : '<tsample=%<SampleTime>>',
                            'Lookup2D'            : '<row=%<x>>\\\\n<column=%<y>>\\\\n<table=%<t>>',
                            'Saturate'            : '<limits=%<upperlimit>\\%<lowerlimit>>',
                            'Backlash'            : '<initial=%<initialoutput>,width=%<backlashwidth>>',
                            'DeadZone'            : '<zone=%<lowervalue>/%<uppervalue>>',
                            'Relay'               : '<low=(%<offswitchvalue>,%<offoutputvalue>)>\\\\n<high=(%<onswitchvalue>,%<onoutputvalue>)>',
                            'Merge'               : '<initial=%<initialoutput>>',
                            'DiscreteTransferFcn' : '<tsample=%<sampleTime>>',
                            'Quantizer'           : '<interval=%<quantizationinterval>>'
                          }

ReusableLibList = ['Asymmetrical Debounce', 'Falling Edge', 'First order filter', 
                   'Hysteresis', 'Latch', 'Periodic enable', 'Rate Limiter', 'Rising edge',
                   'Running average', 'SR Latch', 'Symmetrical Debounce']             

RuleDetails = {
                'MISRA AC SLSF 002' : 'Data type conversion block used for signal data type conversion.',
                'MISRA AC SLSF 003' : 'Fixed step discrete solver used for functional algorithm',
                'MISRA AC SLSF 004' : 'Simulink diagnostic configuration.',
                'MISRA AC SLSF 005 B' : 'Function and duplicate inport blocks must not be used',
                'MISRA AC SLSF 005 C' : 'Data store memory usage must not be used to exchange data across subsystem.',
                'MISRA AC SLSF 006 A' : 'Block parameters evaluation at runtime must not contain Expressions, Data type conversions and Selection of rows or columns.',
                'MISRA AC SLSF 006 B' : 'Block parameters intended to be configured or calibrated must be entered as named constants.',
                'MISRA AC SLSF 006 D' : 'named constants must be defined in an external file',
                'MISRA AC SLSF 006 E' : 'Masked sub-systems must not be used to pass parameters',
                'MISRA AC SLSF 007 A' : 'define explicitly the initialization value.',
                'MISRA AC SLSF 008 A' : 'Saturation property should not be selected if configured to saturate on overflow',
                'MISRA AC SLSF 008 B' : 'Configure rounding behaviour to zero',
                'MISRA AC SLSF 009 B' : 'Block priority should be not used for block execution order',
                'MISRA AC SLSF 009 C' : 'Execution order specified by function calls or data flows.',
                'MISRA AC SLSF 009 D' : 'Sample time to be inherited.',
                'MISRA AC SLSF 011 A' : 'Not more than one level of nested control flow.',
                'MISRA AC SLSF 011 B' : 'Default case, a must in switch case',
                'MISRA AC SLSF 012 A' : 'the control input must be a Boolean type.',
                'MISRA AC SLSF 013 A' : 'at least two switched inputs',
                'MISRA AC SLSF 013 C' : 'Control input must be greater than or equal to 1 and less than switched inputs.',
                'MISRA AC SLSF 014 A' : 'S-functions must be only under certain conditions.',
                'MISRA AC SLSF 015 A' : 'Vector signal:created either by feeding individual named scalar signals into a mux-block, or by using a vector constant, or by a Stateflow block.',
                'MISRA AC SLSF 015 B' : 'Matrix signal:created either by feeding individual vector signals into a matrix concatenation block, or a matrix constant, or by a Stateflow block.',
                'MISRA AC SLSF 015 C' : 'contain signals with common functionality, data type, dimensions and units.',
                'MISRA AC SLSF 016 A' : 'created by using a bus creator block.',
                'MISRA AC SLSF 016 B' : 'must be named.',
                'MISRA AC SLSF 016 C' : 'must not contain unnamed signals.',
                'MISRA AC SLSF 016 D' : 'must only be operated on by bus capable Simulink blocks.',
                'MISRA AC SLSF 016 E' : 'be split up using a bus-selector block and not a demux-block only.',
                'MISRA AC SLSF 017 A' : 'no unconnected blocks.',
                'MISRA AC SLSF 017 B' : 'no unconnected signal lines or busses.',
                'MISRA AC SLSF 018 A' : 'Global and scoped blocks must not be used.',
                'MISRA AC SLSF 018 B' : 'Tag must match corresponding signal or bus label.',
                'MISRA AC SLSF 018 C' : 'tags must be unique.',
                'MISRA AC SLSF 018 D' : '"goto" block must have one or more matching "from" block.',
                'MISRA AC SLSF 018 E' : ' "from" block must have exactly one matching "goto" block.',
                'MISRA AC SLSF 027 A' : 'that require a label must be labelled directly at source.',
                'MISRA AC SLSF 027 B' : 'Propagated labels must be used to redisplay the name.',
                'MISRA AC SLSF 027 C' : 'passing through an inport must be labelled.',
                'MISRA AC SLSF 027 D' : 'passing through an outport must be labelled.',
                'MISRA AC SLSF 027 E' : 'originate from inside a re-useable subsystem must not labelled.',
                'MISRA AC SLSF 027 G' : 'connected to Bus Creator, Goto, Mux, Subsystem, Stateflow Chart must be labelled.',
                'MISRA AC SLSF 027 I' : 'Signal labels or propagated labels must be applied to busses with some conditions.',
                'MISRA AC SLSF 027 J' : 'non-propagated labels must be unique.',
                'MISRA AC SLSF 032 A' : ' port names must still be visible.',
                'MISRA AC SLSF 034 A' : '"C-like bitwise operators" (& and |) must be enabled for all charts.',
                'MISRA AC SLSF 034 C' : '"use strong data typing with Simulink I/O" is selected.',
                'MISRA AC SLSF 034 D' : '"Execute (enter) Chart at Initialization" must be disabled.',
                'MISRA AC SLSF 035 A' : 'The choice of state-chart or flow-chart is driven by the nature of the behaviour being modelled.',
                'MISRA AC SLSF 035 B' : 'Truth tables must not be used.',
                'MISRA AC SLSF 036 A' : 'Bus inputs are not permitted.',
                'MISRA AC SLSF 036 C' : 'name of a Stateflow input/output must be the same as the corresponding signal label.',
                'MISRA AC SLSF 037 A' : 'Must be defined at the chart level or below in the object hierarchy and not at the model level.',
                'MISRA AC SLSF 037 B' : 'local data item name must not be used in different scopes within one state machine.',
                'MISRA AC SLSF 037 G' : 'no unused data items.',
                'MISRA AC SLSF 037 H' : 'must not be set to "Inherit: Same as Simulink".',
                'MISRA AC SLSF 038 C' : 'C library functions must not be used in a state machine. ',
                'MISRA AC SLSF 039 A' : ' a state must have either zero or more than one sub-state.',
                'MISRA AC SLSF 040 B' : 'must not be used as a grouping mechanism',
                'MISRA AC SLSF 040 D' : 'the order of the critical states must be documented in a textbox at the top level of the state machine, wherever critical.',
                'MISRA AC SLSF 041 A' : 'must contain text only.',
                'MISRA AC SLSF 042 A' : 'Super state containing exclusive states must have one default transition.',
                'MISRA AC SLSF 042 B' : 'no more than one default transition',
                'MISRA AC SLSF 042 C' : 'Top level of the state machine must not contain more than one default transitions.',
                'MISRA AC SLSF 042 D' : 'inside a state chart must have ungaurded path to a state.',
                'MISRA AC SLSF 042 E' : 'must not cross state boundaries',
                'MISRA AC SLSF 043 A' : 'condition action and transition action must not be used in the same machine.',
                'MISRA AC SLSF 043 D' : 'semi-colon at the end of each action.',
                'MISRA AC SLSF 043 F' : 'no more than one internal transition from any state',
                'MISRA AC SLSF 043 I' : 'one conditional transition must begin at every junction.',
                'MISRA AC SLSF 043 J' : 'temporal logic must not be used.',
                'MISRA AC SLSF 044 A' : 'during state actions must not be used.',
                'MISRA AC SLSF 044 C' : 'In flow charts state actions must not be used.',
                'MISRA AC SLSF 046 A' : 'History junction must not be used.',
                'MISRA AC SLSF 047 A' : 'local , directed, broadcasted stateflow events, including all implicit eventsmust not be used.',
                'MISRA AC SLSF 047 B' : 'output sateflows must be used only as outputs and not tested internally on transition conditions.',
                'MISRA AC SLSF 048 A' : 'Matlab functions must not be called within state machine.',
                'MISRA AC SLSF 048 B' : 'embedded MATLAB block must not be used.',
                'MISRA AC SLSF 048 C' : 'c code within custom code tab needs to be just pre-processor directives.',
                'MISRA AC SLSF 048 D' : 'pointers to be used only to call external functions.',
                'MISRA AC SLSF 048 E' : 'custom code type needs to be converted to Mathworks type.',
                'MISRA AC SLSF 048 F' : 'custom code must adhere to MISRA C',
                'MISRA AC SLSF 048 G' : 'Numbers other than "0" and "1" must not appear on state machine.',
                'MISRA AC SLSF 052 A' : 'must be unique within state machine.',
                'MISRA AC SLSF 052 B' : 'same name as data should not be given in the chart.',
                'MISRA AC SLSF 053 A' : 'transitions must not be drawn one upon the other.',
                'MISRA AC SLSF 053 J' : 'must contain only one terminating junction.',
                'MISRA AC SLSF 054 A' : 'above horizontal transitions and to the right of vertical transitions.',
                'MISRA AC SLSF 055 A' : 'The order should be entry:, during: and exit: only.',
                'HISL_0002 B' : 'Protect the second input of rem function from going to zero.',
                'HISL_0002 A' : 'Protect the input of reciprocal function from going to zero.',
                'HISL_0003 C' : 'Protect the input from going negative.',
                'HISL_0004 A' : 'Protect the input from going negative.',
                'HISL_0004 B' : 'Protect the input from equalling zero.',
                'HISL_0005 A' : 'InElement-wise(.*) mode, protect all divisor inputs from going to zero.',
                'HISL_0005 B' : 'In Matrix(*) mode, protect all divisor inputs from becoming singular input matrices.',
                'HISL_0005 C' : 'Set the model configuration parameter Diagnostics > Data Validity > Signals > Division by singular matrix to error if Matrix(*) mode selected.',
                'HISL_0008 B' : 'use a block that has a constant value for Iteration limit source, when source is external.',
                'HISL_0010 A' : 'In the block parameter dialog box, select Show else condition.',
                'HISL_0010 B' : 'Connect the outports of the If block to If Action Subsystem blocks.',
                'HISL_0011 B' : 'Connect the outports of the Switch Case block to an Action Subsystem block.',
                'HISL_0011 C' : 'Use an integer data type for the inputs to Switch Case blocks.',
                'HISL_0012 B' : 'avoid using sample time-dependent blocks if the subsystem is called asynchronously',
                'HISL_0013 A' : 'Configuration Parameters dialog box',
                'HISL_0015 B' : 'Specify execution of the conditionally executed subsystems such that in all cases only one subsystem executes during a time step.',
                'HISL_0015 C' : 'Clear the Merge block parameter Allow unequal port widths.',
                'HISL_0021 A' : 'Use a consistent vector indexing method for all blocks. ',
                'HISL_0022 A' : 'for index signals use integer or enum type.',
                'HISL_0022 B' : 'type should cover the range of index.',
                'HISL_0016 A' : 'Avoid comparisons using the == or ~= operator on floating-point data types.',
                'HISL_0017 A' : 'Set the block Output data type parameter to Boolean.',
                'HISL_0018 A' : 'Set the block Output data type parameter to Boolean.',
                'HISL_0019 A' : 'Avoid signed integer data types as input to the block.',
                'HISL_0019 B' : 'Choose an output data type that represents zero exactly.',
                'HISF_0003 A' : 'Avoid signed integer data types as operands to the bitwise operations.',
                'HISF_0010 A' : 'Avoid using these transitions.',
                'HISF_0013 A' : 'Avoid creating transitions that cross from one parallel state to another.',
                'HISF_0014 A' : 'Avoid transition paths that go into and out of a state without ending on a substate.',
                'RP_0008' : 'Important Mask parameters of basic block should be displayed in their attribute format string.',
                'RP_0012' : 'All signals entering and leaving a merge block should have matching name.',
                'RP_0018' : 'input should not be boolean signals',
                'RP_0021' : 'Width of signal inputs must be same.',
                'RP_0028' : 'All events external to Stateflow should be a function call event.',
                'RP_0036' : 'Transition from states must not depend on the implicit clockwise rule.',
                'RP_0037' : 'Not permitted',
                'RP_0046' : 'Not permitted',
                'RP_0051' : 'Data types of signal inputs must be same.',
                'RP_0054' : 'Allowed set of blocks are specified.',
                'RP_0055' : 'Neither condition actions or transition actions should be used in transition between two states.',
                'RP_0056' : 'Default shape and size should be used',
                'RP_0057' : 'Name must be placed below',
                'RP_0058' : 'must be name identical to corresponiding signal or bus name',
                'RP_0059' : 'Shall be present at root level to detail revision history.',
                'RP_0060' : 'Shall be present at root level to feature description.',
                'RP_0061' : 'Look up method "Interpolation - Extrapolation" must not be used.',
                'RP_0062' : 'All outputs from a feature must be displayed',
                'RP_0063' : 'Global parmeters shall not be defined via Model Parameter Configuration Method.',
                'RP_0064' : 'All signals and busses propagating from Blocks must be labelled with propagated signals.'
}


RuleCheckerInput = {
                #TODO : Make it block type rather than property. (See rule in the spreadsheet)
                'MISRA AC SLSF 005 B' : {'ResultType'     : 'NotExist'   										 
                                        },
				
                'MISRA AC SLSF 005 C' : {'Property'       : 'DataStoreMemory',
                                         'Model'          : 'SIMULINK_BLOCK'},
									 
                'MISRA AC SLSF 006 A' : {'srchKeys'        : {'BlockType':['Constant','DiscreteTransferFcn','DiscreteIntegrator','Gain','Lookup2D','Lookup','Relay','Saturate','Switch','UnitDelay','Reference'],'Name':'','SourceType':'Compare To Constant'},														   
                                         'RuleInfo'	        : ['MANUAL CHECK RULE:check the Block Parameter value in Block:','that should not contain Expressions,Data Type Conversions,Selection of Rows and Columns.'],														  
                                         'matchType'        : 'Dynamic'										 
                                        },

                'MISRA AC SLSF 007 A' : {'PropChkData'     : {'X0': '[]'},
                                         'PropChkData1'    : {'InitialOutput': '[]'},
                                         'PropChkData2'    : {'InitialCondition': '[]'},
                                         'PropChkData3'    : {'InitialStates': '[]'},
                                         'UniqueKey'       : ['BlockType', 'Name']
                                        },

                'MISRA AC SLSF 008 A' : {'PropChkData'     : {'SaturateOnIntegerOverflow': 'off'},
                                         'UniqueKey'       : ['BlockType', 'Name']
                                        },

                'MISRA AC SLSF 008 B' : {'PropChkData'     : {'RndMeth': 'Zero'},
                                         'UniqueKey'       : ['BlockType', 'Name'],
                                         'ExcludeBlockLst' : ['Rounding']
                                        },

                'MISRA AC SLSF 009 B' : {'Property'       : 'Priority',
                                         'Model'          : 'SIMULINK_BLOCK'},

                'MISRA AC SLSF 009 D' : {'PropChkData1'    : {'SampleTime': '-1'},
                                         'UniqueKey'       : ['BlockType', 'Name'],
                                         'ExcludeBlockLst' : ['RateTransition', 'UnitDelay',
                                                              'DiscreteIntegrator', 'DiscreteTransferFcn',
                                                              'TriggerPort', 'Outport', 'Inport'],
                                         'PropChkData2'    : {'SystemSampleTime': '-1'},
                                         'ListType'        : 'Block',
                                         'BlockType1'      : 'SubSystem',
                                         'BlockType2'      : 'Reference',
                                         'ResultMatchType' : 'Exact'
                                        },

                'MISRA AC SLSF 011 A' : {'SrcInput'         : {'BlockType' : '#ValueKey#',
                                                               'Name'      : '#MatchKey#'},
                                         'DstInput'         : {'BlockType' : 'If',
                                                               'Name'      : '#MatchKey#'},
                                         'CheckList'        : {'CheckItem' : 'BlockType',
                                                               'CheckValue' : 'If',
                                                               'CheckExp' : 'NOT EQUAL'}
                                        },

                'MISRA AC SLSF 011 B' : {'PropChkData'     : {'ShowDefaultCase': 'on'},
                                         'UniqueKey'       : ['BlockType', 'Name']
                                        },

										
                'MISRA AC SLSF 012' :   {
                                         'UniqueKey'       : ['BlockType', 'Name','Threshold'],
                                         'PropChkData'     : {
                                                              'SourceProp' : 'Criteria',
                                                              },
                                         'ResultMatchType' : 'Match'
                                        },
										
                'MISRA AC SLSF 013 A' : {'ListType'        : 'Block',
                                         'BlockType'       : 'MultiPortSwitch',
                                         'PropChkData'     : {'Inputs': 1},
                                         'UniqueKey'       : ['BlockType', 'Name'],										 
                                         'ResultMatchType' : 'Greater'
                                        },

                'MISRA AC SLSF 013 C' : {'srchKeys'        : {'BlockType':'MultiPortSwitch','Name':''},														   
                                         'RuleInfo'	        : ['MANUAL CHECK RULE:check the control input of MultiPortSwitch Block in:','that value should be greater than or equal to one and not exceed the number of switched inputs.'],														  
                                         'matchType'        : 'blockExist'										 
                                        },
										
                'MISRA AC SLSF 016 A' : {'matchType'       :'Match'
                                        },
										
                'MISRA AC SLSF 016 B' : {'matchType'       :'Exist'
                                        },

                'MISRA AC SLSF 016 C' : {'matchType'       :'NameExist',
                                         'UniqueKey'      :{'BlockType':'BusCreator'}                
                                        },

                'MISRA AC SLSF 016 E' : {'matchType'       :'NotExist'
                                        },

										
                'MISRA AC SLSF 017 A' : {'ListType'        : ['Block','Line',],
                                         'AllowedBlock'     :[['Inport','From','Ground','Constant'],  #only output Blocks
                                                              ['Goto','Outport','Terminator'], #only input Blocks
                                                              ['BusCreator','BusSelector','Mux','Demux','Merge','If','SwitchCase',
                                                               'Concatenate','Reference','Sum','Product','MinMax','Trigonometry',
                                                               'Logic','RelationalOperator','Saturate','DiscreteTransferFcn',
                                                               'TriggerPort','Selector','Math','MultiPortSwitch'                                                               
                                                              ],  # 2D ports,which may vary.                                                             
                                                              ['Lookup','Sqrt','Abs','Gain','UnitDelay','Relay','RateTransition','DataTypeConversion'],#2D vector,fixied size.
                                                              {'Lookup2D':[2,1],
                                                               'Switch':[3,1]
                                                              },
                                                              ['SubSystem'],
                                                              ['DiscreteIntegrator']                                                              
                                                              
                                                             ]
                                        },
										

                'MISRA AC SLSF 017 B' : {'ListType'        : 'Line',
                                         'PropChkData'     : {'SrcBlock': '',
                                                               'DstBlock':'',
                                                              },
                                         'ResultMatchType' : 'Any'
                                        },

                'MISRA AC SLSF 018 A' : {'PropData'        : {'BlockType': 'Goto'},
                                         'CheckListData'   : {'TagVisibility': 'local'},
                                         'ListType'        : 'Block',
                                         'UniqueKey'       : ['BlockType', 'Name'],
                                         'PropChkData'     : {'SourceBlockType': 'From',
                                                              'SourceProp' : 'GotoTag',
                                                              'DestBlockType'  : 'Goto',
                                                              'DestProp'  : 'GotoTag'
                                                              },
                                         'ResultMatchType' : 'Exact'
                                        },

                'MISRA AC SLSF 018 B' : {'PropData'        : {'BlockType': 'Goto'},
                                         'ListType'        : ['Block','Line', 'Port'],
                                         'UniqueKey'       : ['BlockType', 'Name', 'PropagatedSignals'],
                                         'PropChkData'     : {'SourceBlockType': 'From',
                                                              'SourceProp' : 'GotoTag',
                                                              'DestBlockType'  : 'Goto',
                                                              'DestProp'  : 'GotoTag'
                                                              },
                                         'ResultMatchType' : 'Exact'
                                        },
										

                'MISRA AC SLSF 018 C' : {'UniqueKey'       : ['BlockType', 'Name'],
                                         'PropChkData'     : {'SourceBlockType': 'Goto',
                                                              'SourceProp' : 'GotoTag'}
                                        },


                'MISRA AC SLSF 018 D' : {'UniqueKey'       : ['BlockType', 'Name'],
                                         'PropChkData'     : {'SourceBlockType': 'Goto',
                                                               'SourceProp' : 'GotoTag',
                                                               'DestBlockType'  : 'From',
                                                               'DestProp'  : 'GotoTag'
                                                             },
                                         'ResultMatchType' : 'Exist'
                                        },

                'MISRA AC SLSF 018 E' : {'UniqueKey'       : ['BlockType', 'Name'],
                                         'PropChkData'     : {'SourceBlockType': 'From',
                                                               'SourceProp' : 'GotoTag',
                                                               'DestBlockType'  : 'Goto',
                                                               'DestProp'  : 'GotoTag'
                                                             },
                                         'ResultMatchType' : 'Unique'
                                        },
                
                'MISRA AC SLSF 027 A' : {'ListType'        : 'SrcBlock',
                                         'AllowedBlock'     :[['Inport','From','Ground','Constant',
                                                               'Lookup','Sqrt','Abs','Gain','UnitDelay','Relay','RateTransition','DataTypeConversion',
                                                               'Lookup2D','Switch'   
                                                              ],
                                                              ['BusCreator','BusSelector','Mux','Demux','Merge','If','SwitchCase',
                                                               'Concatenate','Reference','Sum','Product','MinMax','Trigonometry',
                                                               'Logic','RelationalOperator','Saturate','DiscreteTransferFcn',
                                                               'TriggerPort','Selector','Math','MultiPortSwitch'                                                               
                                                              ],  # 2D ports,which may vary.                                                             
                                                              ['DiscreteIntegrator']                                                              
                                                              
                                                             ]                                        
                                        },                                         
                                        
                'MISRA AC SLSF 027 C' : { 'ListType'       : ['Line'],
                                          'PropChkData'    : {'BlockType':'Inport',
                                                              'SourceProp':'SrcBlock'},
                                          'ResultMatchType' : 'Inport'
                                        },
                                        
                'MISRA AC SLSF 027 D' : { 'ListType'       : ['Line'],
                                          'PropChkData'    : {'BlockType':'Outport',
                                                              'SourceProp':'DstBlock'},
                                          'ResultMatchType' : 'Outport'
                                        },

                'MISRA AC SLSF 027 E' : {'srchKeys'       : ['BlockType', 'SourceType','Name', 'MaskType'],
                                         'PropChkData'     : ['SrcBlock', 'Name']
                                         },

                'MISRA AC SLSF 027 G' : {
                                         'matchType'       :'NameExist',
                                         'UniqueKey'      :{'BlockType':'BusCreator'},
                                         'UniqueKey2'       : ['BlockType'],
                                         'PropChkData'     : {'SourceProp' : 'Name',
                                                              'BlockProp'  : 'DstBlock'										  
                                                             },
                                         'ResultMatchType' : 'Exist2',
                                         'AllowedBlock'   :['Mux','Goto','SubSystem']		 								 
                                        },
										 
                'MISRA AC SLSF 027 I' : { 'ListType'       : ['Line'],
                                          'PropChkData'    : {'BlockType':'BusCreator',
                                                              'SourceProp':'SrcBlock'},                                          
                                          'PropChkData1'    : {'BlockType':'BusCreator',
                                                              'SourceProp':'DstBlock'},
                                          'PropChkData2'    : {'BlockType':'BusSelector',
                                                              'SourceProp':'SrcBlock'},                                          
                                          'PropChkData3'    : {'BlockType':'BusSelector',
                                                              'SourceProp':'DstBlock'}, 
                                                              
                                          'ResultMatchType' : 'Exist'
                                        },
                                         
                'MISRA AC SLSF 027 J' : {'PropChkData'     : {'SourceBlockType': 'Line',
                                                              'SourceProp' : 'Name'}                                     
                                        },                                         

                'MISRA AC SLSF 034 A' : {'ListType'        : 'chart',
                                         'PropChkData'     : {'actionLanguage': 1},
                                         'ResultMatchType' : 'Exact',
                                         'ListFoundCheck'  : 'FAIL',
                                         'PropFoundCheck'  : 'TRUE'
                                        },

                'MISRA AC SLSF 034 C' : {'ListType'        : 'chart',
                                         'PropChkData'     : {'disableImplicitCasting': 1},
                                         'ResultMatchType' : 'Exact',
                                         'ListFoundCheck'  : 'FAIL',
                                         'PropFoundCheck'  : 'TRUE'
                                        },

                'MISRA AC SLSF 034 D' : {'ListType'        : 'chart',
                                         'PropChkData'     : {'executeAtInitialization': 0},
                                         'ResultMatchType' : 'Exact'
                                        },

                'MISRA AC SLSF 035 B' : {'Property'        : 'truthTable',
                                         'Model'           : 'STATEFLOW'
                                        },
  										
                'MISRA AC SLSF 036 A' : {'srchKeys'        :{'LineSrchKeys':['SrcBlock','Name'],
                                                             'BlckSrchKeys':['OutDataTypeStr','Name'],
                                                             'chartSrchKeys':['Name','Ports','MaskType','MaskDescription']															 
                                                            }
                                        },
										
                'MISRA AC SLSF 036 C' : {'srchKeys'         :{'BlckSrchKeys':['BlockType','Name','Port'],
                                                              'chartSrchKeys':['Name','Ports','MaskType','MaskDescription']			                         
                                                             }				
                                        },
										
										
                'MISRA AC SLSF 037 G' : {'PropChkData'      : {'SourceBlockType': 'data',
                                                               'SourceProp' : 'name',
                                                               'DestBlockType'  : 'state',
                                                               'DestProp'  : 'labelString',
                                                               'DestProp1'  : 'labelString'
                                                              },
                                        },                                        

                'MISRA AC SLSF 037 H' : {'ListType'        : 'data',
                                         'PropChkData'     : {'dataType': 'Inherit: Same as Simulink'},
                                         'ResultMatchType' : 'Opposite'
                                        },

                'MISRA AC SLSF 039 A' : {'ResultType'     : 'Exist'   										 
                                        },
										
                'MISRA AC SLSF 041 A' : {'ListType'         : 'state',
                                         'PropChkData'      : {'type': 'GROUP_STATE'},
                                         'ResultMatchType'  : 'Text'
                                        },

                'MISRA AC SLSF 042 A' : {                                         
                                         'resultType'       :'Exist'										 
                                        },

                'MISRA AC SLSF 042 B' : {                                         
                                         'resultType'       :'Single'										 
                                        },
										
                'MISRA AC SLSF 042 C' : {                                         
                                         'resultType'       :'DefaultAtTop'										 
                                        },
										
                'MISRA AC SLSF 042 D' : {                                         
                                         'resultType'       :'Unguarded_Exist'										 
                                        },

                'MISRA AC SLSF 042 E' : {                                         
                                         'resultType'       :'DefaultTx_Exist'										 
                                        },
										
                'MISRA AC SLSF 043 D' : {                                         
                                         'ChkData'          : ';'
                                        },

                'MISRA AC SLSF 043 A' : {                                         
                                         'srchKeys'          : ['labelString','chart']
                                        },
										
                'MISRA AC SLSF 043 I' : {                                         
                                         'resultType'       :'Unguarded_Exist'										 
                                        },

                'MISRA AC SLSF 043 J' : {
                                         'ChkData'          : ['after', 'before', 'at', 'every', 'temporalCount']
                                        },

                'MISRA AC SLSF 044 A' : {'ListType'         : 'state',
                                         'PropChkData'      : {'labelString': ['during:', 'du:']},
                                         'ResultMatchType'  : 'Contains'
                                        },

                'MISRA AC SLSF 044 C' : {
                                         'ChkData'          : ';'
                                        },

                'MISRA AC SLSF 046 A' : {'ListType'         : 'junction',
                                         'PropChkData'      : {'type': 'HISTORY_JUNCTION'},
                                         'ResultMatchType'  : 'Opposite'
                                        },
										
                'MISRA AC SLSF 048 A' : {'Property'       : 'MATLABFcn',
                                         'Model'          : 'SIMULINK_BLOCK'
                                        },
			
                'MISRA AC SLSF 048 B' : {'ResultType'     : 'Exist',
                                        },

                'MISRA AC SLSF 048 C' : {'ResultType'     : 'Exist',   										 
                                         'RuleInfo'	        :['MANUAL CHECK RULE:C Code with in the custom code tab must be limited to preprocessor statements'],
                                        },
                'MISRA AC SLSF 048 D' : {'ResultType'     : 'Exist',   										 
                                         'RuleInfo'	        :['MANUAL CHECK RULE:Pointers must not be used except when they required to call an external function'],
                                        },
                'MISRA AC SLSF 048 E' : {'ResultType'     : 'Exist',   										 
                                         'RuleInfo'	        :['MANUAL CHECK RULE:Custom code variables must be restricted to fixied width word size datatypes 1)signed 8,16,32 integers(int8_T,int16_T,int32_T) 2)unsigned 8,16,32 integers(uint8_T,uint16_T,uint32_T) 3)32 and 64 bit floating point number(real32_T,real64_T) 4)Bolean(boolean_T)'],
                                        },

                'MISRA AC SLSF 048 F' : {'ResultType'     : 'Exist',   										 
                                         'RuleInfo'	        :['MANUAL CHECK RULE:LDRA Tool checks the MISRA C standards for used custom code,so check the LDRA tool reports'],
                                        },
                                        
                'MISRA AC SLSF 048 G' : {'ListType'         : 'state',
                                         'ListType1'        : 'transition',				
                                         'PropChkData'      : {'labelString': ['0', '1']},
                                         'ResultMatchType'  : 'Otherthan',
                                         'ListFoundCheck'   : 'PASS',
                                         'PropFoundCheck'   : 'FALSE'
                                        },
                                         				
                'MISRA AC SLSF 052 A' : {'PropChkData'      : {'SourceBlockType': 'state',
                                                               'SourceProp' : 'labelString'}
                                        },
                                        
                'MISRA AC SLSF 052 B' : {'PropChkData'      : {'SourceBlockType': 'data',
                                                               'SourceProp' : 'name',
                                                               'DestBlockType'  : 'state',
                                                               'DestProp'  : 'labelString'
                                                              },
                                         'CheckType'        : 'Unique'
                                        },
										
                'MISRA AC SLSF 053 A' : {                                         
                                         'resultType'       :'NotExist'										 
                                        },
										


                'HISL_0002 A'         : {'SrcInput'         : {'BlockType' : '#ValueKey#',
                                                               'Name'      : '#MatchKey#',
                                                               'OutMin' : '#ValueKey#'},
                                         'DstInput'         : {'BlockType' : 'Math',
                                                               'Operator': 'reciprocal',
                                                               'Name'      : '#MatchKey#'},
                                         'CheckList'        : {'CheckExp' : 'MANUAL'}
                                        },
                                                               
                'HISL_0002 B'         : {'srchKeys'         : {'BlockType' : 'Math',
                                                               'Operator'  : ['rem'],
                                                               'Name'      : '' 															   
                                                              },
                                         'RuleInfo'	        :['MANUAL CHECK RULE:check the second input of the rem Block in:','If it is zero,then this rule will fail'],
                                         'matchType'        :'MathExist'										 
                                        },

                'HISL_0003 C'         : {'SrcInput'         : {'BlockType' : '#ValueKey#',
                                                               'Name'      : '#MatchKey#',
                                                               'OutMin' : '#ValueKey#'},
                                         'DstInput'         : {'BlockType' : 'Sqrt',
                                                               'Name'      : '#MatchKey#'},
                                         'CheckList'        : {'CheckItem' : 'OutMin',
                                                               'CheckValue' : 0,
                                                               'CheckExp' : 'GREATER/EQUAL'}
                                        },

                'HISL_0004 A'         : {'srchKeys'        : {'BlockType' : 'Math',
                                                               'Operator'  : ['log','log10'],
                                                               'Name'      : '' 															   
                                                              },
                                         'RuleInfo'	        :['MANUAL CHECK RULE:check the input of the logarithm Block in:','If it is negative,then this rule will fail'],														  
                                         'matchType'        :'MathExist'										 
                                        },
                'HISL_0004 B'         : {'srchKeys'        : {'BlockType' : 'Math',
                                                               'Operator'  : ['log','log10'],
                                                               'Name'      : '' 															   
                                                              },
                                         'RuleInfo'	        :['MANUAL CHECK RULE:check the input of the logarithm Block in:','If it is zero,then this rule will fail'],														  
                                         'matchType'        :'MathExist'										 
                                        },
										                                             
                'HISL_0005 A'         : {'srchKeys'        : {'BlockType':'Product','Multiplication':'','Name':'','Inputs':''},														   
                                         'RuleInfo'	        : ['MANUAL CHECK RULE:check the input of divisor port in Product Block in:','If it is zero,then this rule will fail'],														  
                                         'matchType'        : 'ProductExist'										 
                                        },

                'HISL_0005 B'         : {'srchKeys'        :{'BlockType':'Product','Multiplication':'','Name':'','Inputs':''},
                                         'RuleInfo'	        :['MANUAL CHECK RULE:check the input signal of the divisor port in Product Block in:','If it is singular input matrices,then this rule will fail'],														  
                                         'matchType'        :'ProductExist'										 
                                        },

                'HISL_0010 A'         : {'PropChkData'     : {'ShowElse': 'on'},
                                         'UniqueKey'       : ['BlockType', 'Name','ElseIfExpressions'],
                                         'ListType'        : 'Block',
                                         'BlockType'       : 'If',
                                         'ResultMatchType' : 'Exact'
                                        },

                'HISL_0010 B'         : {'PropChkData'     : {'DstPort': 'ifaction'},
                                         'blockType'       : 'IfExist', 				
                                         'UniqueKey'       : ['BlockType', 'Name','Ports','ElseIfExpressions']
                                        },
                										
                'HISL_0011 B'         : {'PropChkData'     : {'DstPort': 'ifaction'},
                                         'blockType'       : 'SwitchCaseExist',				
                                         'UniqueKey'       : ['BlockType', 'Name','Ports']
                                        },

                'HISL_0011 C'         : {'srchKeys'        : {'BlockType':'SwitchCase','Name':''},														   
                                         'RuleInfo'	        : ['MANUAL CHECK RULE:check the input of SwitchCase Block in:','If it is not a integer datatype,then this rule will fail'],														  
                                         'matchType'        : 'blockExist'										 
                                        },
                                        
                'HISL_0015 B'         : {'srchKeys'        : {'BlockType':'Merge','Name':''},														   
                                         'RuleInfo'	        : ['MANUAL CHECK RULE:If two or more inputs of Merge Block in:',' are coming from conditionally excuted subSystems, then such inputs must have mutual exclusion between the conditionally executed subsystems feeding a Merge block'],														  
                                         'matchType'        : 'blockExist'										 
                                        },

                'HISL_0015 C'         : {'PropChkData'     : {'AllowUnequalInputPortWidths': 'off'},
                                         'UniqueKey'       : ['BlockType', 'Name'],
                                         'ListType'        : 'Block',
                                         'BlockType'       : 'Merge',
                                         'ResultMatchType' : 'Exact'
                                        },

                'HISL_0016 A'         : {'srchKeys'        : {'BlockType':'RelationalOperator','Operator':['==','~='],'Name':''},														   
                                         'RuleInfo'	        : ['MANUAL CHECK RULE:check the input signals of RelationalOperator Block in:','If input signals are float type,then this rule will fail'],														  
                                         'matchType'        : 'Exist'										 
                                        },
										
                'HISL_0017 A'         : {
                                         'UniqueKey'       : {'BlockType':'RelationalOperator'},
                                         'SrchKeys'        : ['BlockType','OutDataTypeStr','Name']
                                        },
										
                'HISL_0018 A'         : {
                                         'UniqueKey'       : {'BlockType':'Logic'},
                                         'SrchKeys'        : ['BlockType','OutDataTypeStr','Name']
                                        },

                'HISL_0019 A'         : {'srchKeys'        : {'BlockType':'Reference','SourceType':['Bitwise Operator'],'Name':''},														   
                                         'RuleInfo'	        : ['MANUAL CHECK RULE:check the input signals of Bitwise Operator Block in:','If input signals are signed integer data type,then this rule will fail'],														  
                                         'matchType'        : 'Exist'										 
                                        },

										
                'HISL_0019 B'         : {'PropData'         : {'BlockType': 'Reference',
                                                               'SourceType': 'Bitwise Operator'},
                                         'CheckListData'    : {'BitMaskRealWorld' : 'Stored Integer'},
                                         'ListType'         : 'Block'
                                        },

                'HISF_0003 A'         : {'SrcInput'         : {'BlockType' : '#ValueKey#',
                                                               'Name'      : '#MatchKey#',
                                                               'OutDataTypeStr' : '#ValueKey#'},
                                         'DstInput'         : {'BlockType' : 'Reference',
                                                               'SourceType': 'Bitwise Operator',
                                                               'Name'      : '#MatchKey#'},
                                         'CheckList'        : {'CheckItem' : 'OutDataTypeStr',
                                                               'CheckValue' : ['uint8', 'uint16','uint32'],
                                                               'CheckExp' : 'WITHIN'}
                                        },
										
                'RP_0012'             : {
                                         'UniqueKey'       : ['BlockType', 'Name'],
                                         'PropChkData'     : {
                                                              'SourceProp' : 'Ports',
                                                             },
                                         'ResultMatchType' : 'Unique'
                                        },
										
                                        
                'RP_0018'             : {'SrcInput'         : {'BlockType' : '#ValueKey#',
                                                               'Name'      : '#MatchKey#'},
                                         'DstInput'         : {'BlockType' : 'RelationalOperator',
                                                               'Name'      : '#MatchKey#'},
                                         'CheckList'        : {'CheckItem' : 'OutDataTypeStr',
                                                               'CheckValue' : 'Boolean',
                                                               'CheckExp' : 'NOT EQUAL'}
                                        },
                                        
                'RP_0021'             : {'PropChkData'     : {'AllowDiffInputSizes': 'off'},
                                         'UniqueKey'       : ['BlockType', 'Name'],
                                         'ListType'        : 'Block',
                                         'BlockType'       : 'Switch',
                                         'ResultMatchType' : 'Exact'
                                        },

                'RP_0028'             : {'srchKeys_chart'  :['id','name'],
                                         'srchKeys_event'  :['name','linkNode','scope','trigger']
                                        },

                'RP_0036'             : {'ListType'        : 'chart',
                                         'PropChkData'     : {'userSpecifiedStateTransitionExecutionOrder': 1},
                                         'ResultMatchType' : 'Exact',
                                         'ListFoundCheck'  : 'FAIL',
                                         'PropFoundCheck'  : 'TRUE'
                                        },

                'RP_0037'             : {                                         
                                         'ChkData'          : ';'
                                        },
                                        
                'RP_0046'             : {'ListType'         : 'state',
                                         'ListType1'        : 'transition',				
                                         'PropChkData'      : {'labelString': []},
                                         'ResultMatchType'  : 'DoesNotContain',
                                        },
                
                'RP_0051'             : {'PropChkData'    : {'InputSameDT': 'on'},
                                         'UniqueKey'       : ['BlockType', 'Name'],
                                         'ListType'        : 'Block',
                                         'BlockType1'      : 'Switch',
                                         'BlockType2'      : 'MultiPortSwitch',
                                         'ResultMatchType' : 'Exact'
                                        },
                                        
                'RP_0055'             : {'ListType'         : 'transition',
                                         'PropChkData'      : {'labelString': [';']},
                                         'ResultMatchType'  : 'Contains',
                                         'ListFoundCheck'   : 'PASS',
                                         'PropFoundCheck'   : 'TRUE'
                                        },
                                        
                'RP_0057'             : {'Property'        : 'NamePlacement',
                                         'Model'           : 'SIMULINK_BLOCK'
                                        },
                                        
                'RP_0058'             : { 'matchType'       :'Exact',
                                         'UniqueKey'      :{'BlockType':'Inport'},
                                         'UniqueKey2'      :{'BlockType':'Outport'}                                          
                                        },

                'RP_0059'             : {'SrchKeys'        : ['BlockType','SourceType','ECoderFlag'],
                                         'PropChkData'      : {'ECoderFlag': 'History'} 				 
                                        },

                'RP_0060'             : {'SrchKeys'        : ['BlockType','SourceType','ECoderFlag'],
                                         'PropChkData'      : {'ECoderFlag': 'Description'} 
                                        },

                'RP_0061'             : {'PropChkData'     : {'LookUpMeth': 'Interpolation-Extrapolation'},
                                         'UniqueKey'       : ['BlockType', 'Name']
                                        },                                                                  

                'RP_0063'             : {'Property'        : 'TunableVars',
                                         'Model'           : 'SIMULINK_MODEL'
                                        },

                'RP_0064'             : {
                                         'UniqueKey'       : ['BlockType'],
                                         'PropChkData'     : {'SourceProp' : 'Name',
                                                              'BlockProp'  : 'SrcBlock'
                                                             },
                                         'ResultMatchType' : 'Exist',
                                         'AllowedBlock'   : ['From','SubSystem','Demux','Selector']										 
                                        }
										
										
                }

configReferenceFiles = {
                'mdlref10ms_cs'  : 'Z:\IAI-TXB-HLC\Dynamic\Models\Simulink_Localisation\SimulinkCommon\mdl_config_sets/taxibot_10ms_mdlref_config_set.m',
                'context10ms_cs' : 'Z:\IAI-TXB-HLC\Dynamic\Models\Simulink_Localisation\SimulinkCommon\mdl_config_sets/taxibot_10ms_context_config_set.m',
                'mdlref50ms_cs'  : 'Z:\IAI-TXB-HLC\Dynamic\Models\Simulink_Localisation\SimulinkCommon\mdl_config_sets/taxibot_50ms_mdlref_config_set.m',
                'context50ms_cs' : 'Z:\IAI-TXB-HLC\Dynamic\Models\Simulink_Localisation\SimulinkCommon\mdl_config_sets/taxibot_50ms_context_config_set.m',
                'lib_cs'         : 'Z:\IAI-TXB-HLC\Dynamic\Models\Simulink_Localisation\SimulinkCommon\mdl_config_sets/taxibot_libraryMdlRef_config_set.m'}
