# -*- coding: utf-8 -*-
'''
#inspered by author: sabbi

#11/10/2021
'''


import ctypes
import numpy as np
import os
# import cv2
import threading
import time

os.environ["GENICAM_ROOT_V2_4"] = "/opt/pleora/ebus_sdk/x86_64/lib/genicam/"	#declaration needed for Linux SDK

lock = threading.Lock()

def calcParam(v,c,n):
	return (((c)<<24)+((v)<<16)+(n))


PicamValueType = {
    "Integer": 1,
    "Boolean": 3,
    "Enumeration": 4,
    "LargeInteger": 6,
    "FloatingPoint": 2,
    "Rois": 5,
    "Pulse": 7,
    "Modulations": 8
}
PicamValueTypeLookup = dict(zip(PicamValueType.values(), PicamValueType.keys()))

PicamConstraintType = {
    "None": 1,
    "Range": 2,
    "Collection": 3,
    "Rois": 4,
    "Pulse": 5,
    "Modulations": 6
}
PicamConstraintTypeLookup = dict(zip(PicamConstraintType.values(), PicamConstraintType.keys()))

PI_V = lambda v, c, n: (PicamConstraintType[c] << 24) + (PicamValueType[v] << 16) + n

PicamParameter = {
   "PicamParameter_ExposureTime"                      :PI_V("FloatingPoint", "Range",        23),
   "PicamParameter_ShutterTimingMode"                 : PI_V("Enumeration",   "Collection",   24),
   "PicamParameter_ShutterOpeningDelay"               : PI_V("FloatingPoint", "Range",        46),
   "PicamParameter_ShutterClosingDelay"               : PI_V("FloatingPoint", "Range",        25),
   "PicamParameter_ShutterDelayResolution"            : PI_V("FloatingPoint", "Collection",   47),
   "PicamParameter_InternalShutterType"             : PI_V("Enumeration",   "None",        139),
   "PicamParameter_InternalShutterStatus"           : PI_V("Enumeration",   "None",        153),
   "PicamParameter_ExternalShutterType"           : PI_V("Enumeration",   "None",        152),
   "PicamParameter_ExternalShutterStatus"          : PI_V("Enumeration",   "None",        154),
   "PicamParameter_ActiveShutter"                     : PI_V("Enumeration",   "Collection",  155),
   "PicamParameter_InactiveShutterTimingModeResult"   : PI_V("Enumeration",   "None",        156),
   "PicamParameter_GatingMode"                        : PI_V("Enumeration",   "Collection",   93),
   "PicamParameter_RepetitiveGate"                    : PI_V("Pulse",         "Pulse",        94),
   "PicamParameter_SequentialStartingGate"            : PI_V("Pulse",         "Pulse",        95),
   "PicamParameter_SequentialEndingGate"              : PI_V("Pulse",         "Pulse",        96),
   "PicamParameter_SequentialGateStepCount"           : PI_V("LargeInteger",  "Range",        97),
   "PicamParameter_SequentialGateStepIterations"      : PI_V("LargeInteger",  "Range",        98),
   "PicamParameter_DifStartingGate"                   : PI_V("Pulse",         "Pulse",       102),
   "PicamParameter_DifEndingGate"                     : PI_V("Pulse",         "Pulse",       103),
   "PicamParameter_EnableIntensifier"                 : PI_V("Boolean",       "Collection",   86),
   "PicamParameter_IntensifierStatus"                 : PI_V("Enumeration",   "None",         87),
   "PicamParameter_IntensifierGain"                   : PI_V("Integer",       "Range",        88),
   "PicamParameter_EMIccdGainControlMode"             : PI_V("Enumeration",   "Collection",  123),
   "PicamParameter_EMIccdGain"                        : PI_V("Integer",       "Range",       124),
   "PicamParameter_PhosphorDecayDelay"                : PI_V("FloatingPoint", "Range",        89),
   "PicamParameter_PhosphorDecayDelayResolution_"      : PI_V("FloatingPoint", "Collection",   90),
   "PicamParameter_BracketGating"                     : PI_V("Boolean",       "Collection",  100),
   "PicamParameter_IntensifierOptions"                : PI_V("Enumeration",   "None",        101),
   "PicamParameter_EnableModulation"                  : PI_V("Boolean",       "Collection",  111),
   "PicamParameter_ModulationDuration"                : PI_V("FloatingPoint", "Range",       118),
   "PicamParameter_ModulationFrequency"               : PI_V("FloatingPoint", "Range",       112),
   "PicamParameter_RepetitiveModulationPhase"         : PI_V("FloatingPoint", "Range",       113),
   "PicamParameter_SequentialStartingModulationPhase" : PI_V("FloatingPoint", "Range",       114),
   "PicamParameter_SequentialEndingModulationPhase"   : PI_V("FloatingPoint", "Range",       115),
   "PicamParameter_CustomModulationSequence"          : PI_V("Modulations",   "Modulations", 119),
   "PicamParameter_PhotocathodeSensitivity"           : PI_V("Enumeration",   "None",        107),
   "PicamParameter_GatingSpeed"                       : PI_V("Enumeration",   "None",        108),
   "PicamParameter_PhosphorType"                      : PI_V("Enumeration",   "None",        109),
   "PicamParameter_IntensifierDiameter"               : PI_V("FloatingPoint", "None",        110),
   "PicamParameter_AdcSpeed"                          : PI_V("FloatingPoint", "Collection",   33),
   "PicamParameter_AdcBitDepth"                       : PI_V("Integer",       "Collection",   34),
   "PicamParameter_AdcAnalogGain"                     : PI_V("Enumeration",   "Collection",   35),
   "PicamParameter_AdcQuality"                        : PI_V("Enumeration",   "Collection",   36),
   "PicamParameter_AdcEMGain"                         : PI_V("Integer",       "Range",        53),
   "PicamParameter_CorrectPixelBias"                  : PI_V("Boolean",       "Collection",  106),
   "PicamParameter_TriggerSource"                     : PI_V("Enumeration",   "Collection",   79),
   "PicamParameter_TriggerResponse"                   : PI_V("Enumeration",   "Collection",   30),
   "PicamParameter_TriggerDetermination"              : PI_V("Enumeration",   "Collection",   31),
   "PicamParameter_TriggerFrequency"                  : PI_V("FloatingPoint", "Range",        80),
   "PicamParameter_TriggerTermination"                : PI_V("Enumeration",   "Collection",   81),
   "PicamParameter_TriggerCoupling"                   : PI_V("Enumeration",   "Collection",   82),
   "PicamParameter_TriggerThreshold"                  : PI_V("FloatingPoint", "Range",        83),
   "PicamParameter_TriggerDelay"                      : PI_V("FloatingPoint", "Range",       164),
   "PicamParameter_OutputSignal"                      : PI_V("Enumeration",   "Collection",   32),
   "PicamParameter_InvertOutputSignal"                : PI_V("Boolean",       "Collection",   52),
   "PicamParameter_OutputSignal2"                     : PI_V("Enumeration",   "Collection",  150),
   "PicamParameter_InvertOutputSignal2"               : PI_V("Boolean",       "Collection",  151),
   "PicamParameter_EnableAuxOutput"                  : PI_V("Boolean",       "Collection",  161),
   "PicamParameter_AuxOutput"                         : PI_V("Pulse",         "Pulse",        91),
   "PicamParameter_EnableSyncMaster"                  : PI_V("Boolean",       "Collection",   84),
   "PicamParameter_SyncMaster2Delay"                  : PI_V("FloatingPoint", "Range",        85),
   "PicamParameter_EnableModulationOutputSignal"      : PI_V("Boolean",       "Collection",  116),
   "PicamParameter_ModulationOutputSignalFrequency"   : PI_V("FloatingPoint", "Range",       117),
   "PicamParameter_ModulationOutputSignalAmplitude"   : PI_V("FloatingPoint", "Range",       120),
   "PicamParameter_AnticipateTrigger"                 : PI_V("Boolean",       "Collection",  131),
   "PicamParameter_DelayFromPreTrigger"               : PI_V("FloatingPoint", "Range",       132),
   "PicamParameter_ReadoutControlMode"                : PI_V("Enumeration",   "Collection",   26),
   "PicamParameter_ReadoutTimeCalculation"            : PI_V("FloatingPoint", "None",         27),
   "PicamParameter_ReadoutPortCount"                  : PI_V("Integer",       "Collection",   28),
   "PicamParameter_ReadoutOrientation"                : PI_V("Enumeration",   "None",         54),
   "PicamParameter_KineticsWindowHeight"              : PI_V("Integer",       "Range",        56),
   "PicamParameter_SeNsRWindowHeight"                 : PI_V("Integer",       "Range",       163),
   "PicamParameter_VerticalShiftRate"                 : PI_V("FloatingPoint", "Collection",   13),
   "PicamParameter_Accumulations"                     : PI_V("LargeInteger",  "Range",        92),
   "PicamParameter_EnableNondestructiveReadout"       : PI_V("Boolean",       "Collection",  128),
   "PicamParameter_NondestructiveReadoutPeriod"       : PI_V("FloatingPoint", "Range",       129),
   "PicamParameter_Rois"                              : PI_V("Rois",          "Rois",         37),
   "PicamParameter_NormalizeOrientation"              : PI_V("Boolean",       "Collection",   39),
   "PicamParameter_DisableDataFormatting"             : PI_V("Boolean",       "Collection",   55),
   "PicamParameter_ReadoutCount"                      : PI_V("LargeInteger",  "Range",        40),
   "PicamParameter_ExactReadoutCountMaximum"          : PI_V("LargeInteger",  "None",         77),
   "PicamParameter_PhotonDetectionMode"               : PI_V("Enumeration",   "Collection",  125),
   "PicamParameter_PhotonDetectionThreshold"          : PI_V("FloatingPoint", "Range",       126),
   "PicamParameter_PixelFormat"                       : PI_V("Enumeration",   "Collection",   41),
   "PicamParameter_FrameSize"                         : PI_V("Integer",       "None",         42),
   "PicamParameter_FrameStride"                       : PI_V("Integer",       "None",         43),
   "PicamParameter_FramesPerReadout"                  : PI_V("Integer",       "None",         44),
   "PicamParameter_ReadoutStride"                     : PI_V("Integer",       "None",         45),
   "PicamParameter_PixelBitDepth"                     : PI_V("Integer",       "None",         48),
   "PicamParameter_ReadoutRateCalculation"            : PI_V("FloatingPoint", "None",         50),
   "PicamParameter_OnlineReadoutRateCalculation"      : PI_V("FloatingPoint", "None",         99),
   "PicamParameter_FrameRateCalculation"              : PI_V("FloatingPoint", "None",         51),
   "PicamParameter_Orientation"                       : PI_V("Enumeration",   "None",         38),
   "PicamParameter_TimeStamps"                        : PI_V("Enumeration",   "Collection",   68),
   "PicamParameter_TimeStampResolution"               : PI_V("LargeInteger",  "Collection",   69),
   "PicamParameter_TimeStampBitDepth"                 : PI_V("Integer",       "Collection",   70),
   "PicamParameter_TrackFrames"                       : PI_V("Boolean",       "Collection",   71),
   "PicamParameter_FrameTrackingBitDepth"             : PI_V("Integer",       "Collection",   72),
   "PicamParameter_GateTracking"                      : PI_V("Enumeration",   "Collection",  104),
   "PicamParameter_GateTrackingBitDepth"              : PI_V("Integer",       "Collection",  105),
   "PicamParameter_ModulationTracking"                : PI_V("Enumeration",   "Collection",  121),
   "PicamParameter_ModulationTrackingBitDepth"        : PI_V("Integer",       "Collection",  122),
   "PicamParameter_SensorType"                        : PI_V("Enumeration",   "None",         57),
   "PicamParameter_CcdCharacteristics"                : PI_V("Enumeration",   "None",         58),
   "PicamParameter_SensorActiveWidth"                 : PI_V("Integer",       "None",         59),
   "PicamParameter_SensorActiveHeight"                : PI_V("Integer",       "None",         60),
   "PicamParameter_SensorActiveExtendedHeight"        : PI_V("Integer",       "None",        159),
   "PicamParameter_SensorActiveLeftMargin"            : PI_V("Integer",       "None",         61),
   "PicamParameter_SensorActiveTopMargin"             : PI_V("Integer",       "None",         62),
   "PicamParameter_SensorActiveRightMargin"           : PI_V("Integer",       "None",         63),
   "PicamParameter_SensorActiveBottomMargin"          : PI_V("Integer",       "None",         64),
   "PicamParameter_SensorMaskedHeight"                : PI_V("Integer",       "None",         65),
   "PicamParameter_SensorMaskedTopMargin"             : PI_V("Integer",       "None",         66),
   "PicamParameter_SensorMaskedBottomMargin"          : PI_V("Integer",       "None",         67),
   "PicamParameter_SensorSecondaryMaskedHeight"       : PI_V("Integer",       "None",         49),
   "PicamParameter_SensorSecondaryActiveHeight"       : PI_V("Integer",       "None",         74),
   "PicamParameter_PixelWidth"                        : PI_V("FloatingPoint", "None",          9),
   "PicamParameter_PixelHeight"                       : PI_V("FloatingPoint", "None",         10),
   "PicamParameter_PixelGapWidth"                     : PI_V("FloatingPoint", "None",         11),
   "PicamParameter_PixelGapHeight"                    : PI_V("FloatingPoint", "None",         12),
   "PicamParameter_ApplicableStarDefectMapID"         : PI_V("Integer",       "None",        166),
   "PicamParameter_ActiveWidth"                       : PI_V("Integer",       "Range",         1),
   "PicamParameter_ActiveHeight"                      : PI_V("Integer",       "Range",         2),
   "PicamParameter_ActiveExtendedHeight"              : PI_V("Integer",       "Range",       160),
   "PicamParameter_ActiveLeftMargin"                  : PI_V("Integer",       "Range",         3),
   "PicamParameter_ActiveTopMargin"                   : PI_V("Integer",       "Range",         4),
   "PicamParameter_ActiveRightMargin"                 : PI_V("Integer",       "Range",         5),
   "PicamParameter_ActiveBottomMargin"                : PI_V("Integer",       "Range",         6),
   "PicamParameter_MaskedHeight"                      : PI_V("Integer",       "Range",         7),
   "PicamParameter_MaskedTopMargin"                   : PI_V("Integer",       "Range",         8),
   "PicamParameter_MaskedBottomMargin"                : PI_V("Integer",       "Range",        73),
   "PicamParameter_SecondaryMaskedHeight"             : PI_V("Integer",       "Range",        75),
   "PicamParameter_SecondaryActiveHeight"             : PI_V("Integer",       "Range",        76),
   "PicamParameter_CleanSectionFinalHeight"           : PI_V("Integer",       "Range",        17),
   "PicamParameter_CleanSectionFinalHeightCount"      : PI_V("Integer",       "Range",        18),
   "PicamParameter_CleanSerialRegister"               : PI_V("Boolean",       "Collection",   19),
   "PicamParameter_CleanCycleCount"                   : PI_V("Integer",       "Range",        20),
   "PicamParameter_CleanCycleHeight"                  : PI_V("Integer",       "Range",        21),
   "PicamParameter_CleanBeforeExposure"               : PI_V("Boolean",       "Collection",   78),
   "PicamParameter_CleanUntilTrigger"                 : PI_V("Boolean",       "Collection",   22),
   "PicamParameter_StopCleaningOnPreTrigger"          : PI_V("Boolean",       "Collection",  130),
   "PicamParameter_SensorTemperatureSetPoint"         : PI_V("FloatingPoint", "Range",        14),
   "PicamParameter_SensorTemperatureReading"          : PI_V("FloatingPoint", "None",         15),
   "PicamParameter_SensorTemperatureStatus"           : PI_V("Enumeration",   "None",         16),
   "PicamParameter_DisableCoolingFan"                 : PI_V("Boolean",       "Collection",   29),
   "PicamParameter_CoolingFanStatus"                  : PI_V("Enumeration",   "None",        162),
   "PicamParameter_EnableSensorWindowHeater"          : PI_V("Boolean",       "Collection",  127),
   "PicamParameter_VacuumStatus"                      : PI_V("Enumeration",   "None",        165),
   "PicamParameter_CenterWavelengthSetPoint"          : PI_V("FloatingPoint", "Range",       140),
   "PicamParameter_CenterWavelengthReading"           : PI_V("FloatingPoint", "None",        141),
   "PicamParameter_CenterWavelengthStatus"            : PI_V("Enumeration",   "None",        149),
   "PicamParameter_GratingType"                       : PI_V("Enumeration",   "None",        142),
   "PicamParameter_GratingCoating"                    : PI_V("Enumeration",   "None",        143),
   "PicamParameter_GratingGrooveDensity"              : PI_V("FloatingPoint", "None",        144),
   "PicamParameter_GratingBlazingWavelength"          : PI_V("FloatingPoint", "None",        145),
   "PicamParameter_FocalLength"                       : PI_V("FloatingPoint", "None",        146),
   "PicamParameter_InclusionAngle"                    : PI_V("FloatingPoint", "None",        147),
   "PicamParameter_SensorAngle"                       : PI_V("FloatingPoint", "None",        148),
   "PicamParameter_LaserOutputMode"                   : PI_V("Enumeration",   "Collection",  137),
   "PicamParameter_LaserPower"                        : PI_V("FloatingPoint", "Range",       138),
   "PicamParameter_LaserWavelength"                   : PI_V("FloatingPoint", "None",        167),
   "PicamParameter_LaserStatus"                       : PI_V("Enumeration",   "None",        157),
   "PicamParameter_InputTriggerStatus"                : PI_V("Enumeration",   "None",        158),
   "PicamParameter_LightSource"                       : PI_V("Enumeration",   "Collection",  133),
   "PicamParameter_LightSourceStatus"                 : PI_V("Enumeration",   "None",        134),
   "PicamParameter_Age  "                             : PI_V("FloatingPoint", "None",        135),
   "PicamParameter_LifeExpectancy"                    : PI_V("FloatingPoint", "None",        136)
}    
    
PicamValueAccess = {
    "ReadOnly": 1,
    "ReadWriteTrivial": 3,
    "ReadWrite": 2
}
PicamValueAccessLookup = dict(zip(PicamValueAccess.values(), PicamValueAccess.keys()))    
PicamStringSize = {
    "SensorName": 64,
    "SerialNumber": 64,
    "FirmwareName": 64,
    "FirmwareDetail": 256
}
PicamStringSizeLookup = dict(zip(PicamStringSize.values(), PicamStringSize.keys()))    
#check picam.h for parameter definitions
# paramFrames = ctypes.c_int(calcParam(6,2,40))	#PicamParameter_ReadoutCount
# paramStride = ctypes.c_int(calcParam(1,1,45))	#PicamParameter_ReadoutStride
# paramROIs = ctypes.c_int(calcParam(5, 4, 37))	#PicamParameter_Rois
# paramReadRate=ctypes.c_int(calcParam(2,1,50))	#PicamParameter_ReadoutRateCalculation
# paramExpose=ctypes.c_int(calcParam(2,2,23))		#PicamParameter_ExposureTime
paramFrames = ctypes.c_int(calcParam(6,2,40))    #PicamParameter_ReadoutCount
'''PicamParameter_ReadoutCount'''
paramStride = ctypes.c_int(calcParam(1,1,45))    #PicamParameter_ReadoutStride
paramFrameSize = ctypes.c_int(calcParam(1,1,42))
paramFrameStride = ctypes.c_int(calcParam(1,1,43))
paramFramesPerRead = ctypes.c_int(calcParam(1,1,44))
paramROIs = ctypes.c_int(calcParam(5, 4, 37))    #PicamParameter_Rois
paramReadRate=ctypes.c_int(calcParam(2,1,50))    #PicamParameter_ReadoutRateCalculation
paramExpose=ctypes.c_int(calcParam(2,2,23))        #PicamParameter_ExposureTime
paramRepetitiveGate=ctypes.c_int(calcParam(7,5,94))
paramReadoutControlMode=ctypes.c_int(calcParam(4,3,26))
paramActiveWidth=ctypes.c_int(calcParam(1,2,1))
paramActiveHeight=ctypes.c_int(calcParam(1,2,2))
paramTopMargin=ctypes.c_int(calcParam(1,2,4))
paramBottomMargin=ctypes.c_int(calcParam(1,2,6))
paramLeftMargin=ctypes.c_int(calcParam(1,2,3))
paramRightMargin=ctypes.c_int(calcParam(1,2,5))
paramMaskHeight=ctypes.c_int(calcParam(1,2,7))
paramMaskTopMargin=ctypes.c_int(calcParam(1,2,8))
paramMaskBottomMargin=ctypes.c_int(calcParam(1,2,73))
paramCorrectPixelBias=ctypes.c_int(calcParam(3,3,106))
paramVerticalShiftRate=ctypes.c_int(calcParam(2,3,13))
paramCleanUntilTrigger=ctypes.c_int(calcParam(3,3,22))
paramCleanSerialRegister=ctypes.c_int(calcParam(3,3,19))
paramCleanBeforeExposure=ctypes.c_int(calcParam(3,3,78))
paramAdcSpeed=ctypes.c_int(calcParam(2,3,33))
paramAdcQuality=ctypes.c_int(calcParam(4,3,36))
paramAdcGain=ctypes.c_int(calcParam(4,3,35))
paramAdcBitDepth=ctypes.c_int(calcParam(1,3,34))
paramReadoutPortCount=ctypes.c_int(calcParam(1,3,28))
paramSensorActiveWidth = ctypes.c_int(calcParam(1,1,59))
paramSensorActiveHeight = ctypes.c_int(calcParam(1,1,60))
paramShutterClosingDelay=ctypes.c_int(calcParam(2,2,25))
paramShutterOpeningDelay=ctypes.c_int(calcParam(2,2,46))
paramSensorTemperatureReading = ctypes.c_int(calcParam(2,1,15))
paramSensorTemperatureSetPoint = ctypes.c_int(calcParam(2,2,14))
paramSensorTemperatureStatus = ctypes.c_int(calcParam(4,1,16))

#metadata related
paramTimeStamps = ctypes.c_int(calcParam(4,3,68))
paramTimeStampResolution = ctypes.c_int(calcParam(6,3,69))
paramTimeStampBitDepth = ctypes.c_int(calcParam(1,3,70))
paramTrackFrames = ctypes.c_int(calcParam(3,3,71))
paramFrameTrackingBitDepth = ctypes.c_int(calcParam(1,3,72))
#opencv related functions
def WindowSize(numRows,numCols):
	aspect = 1
	if numRows > 1080:
		aspect = int(numRows/1080)
	elif numCols > 1920:
		aspect = int(numCols/1920)
	winWidth = int(numCols/aspect)
	winHeight = int(numRows/aspect)
	return winWidth, winHeight


class camIDStruct(ctypes.Structure):
	_fields_=[
		('model', ctypes.c_int),
		('computer_interface', ctypes.c_int),
		('sensor_name', ctypes.c_char * 64),
		('serial_number', ctypes.c_char * 64)]

class availableData(ctypes.Structure):
	_fields_=[
		('initial_readout', ctypes.c_void_p),
		('readout_count', ctypes.c_longlong)]

class acqStatus(ctypes.Structure):
        _fields_=[
            ('running', ctypes.c_bool),
            ('errors', ctypes.c_int),
            ('readout_rate',ctypes.c_double)]

class acqBuf(ctypes.Structure):
        _fields_=[
            ('memory', ctypes.c_void_p),
            ('memory_size',ctypes.c_longlong)]

class roiStruct(ctypes.Structure):
	_fields_=[
		('x', ctypes.c_int),
		('width', ctypes.c_int),
		('x_binning', ctypes.c_int),
		('y', ctypes.c_int),
		('height', ctypes.c_int),
		('y_binning', ctypes.c_int)]

class roisStruct(ctypes.Structure):
	_fields_=[
		('roi_array', ctypes.c_void_p),
		('roi_count', ctypes.c_int)]

class PicamPulse(ctypes.Structure):
    _fields_ = [("delay", ctypes.c_double),
                ("width", ctypes.c_double)]


class PicamModulation(ctypes.Structure):
    _fields_ = [("duration", ctypes.c_double),
                ("frequency", ctypes.c_double),
                ("phase", ctypes.c_double),
                ("output_signal_frequency", ctypes.c_double)]
class PicamModulations(ctypes.Structure):
    _fields_ = [("modulation_array", ctypes.POINTER(PicamModulation)),
                ("modulation_count", ctypes.c_int)]
   
class PicamCameraID(ctypes.Structure):
        _fields_ = [("model",  ctypes.c_int),
                    ("computer_interface",  ctypes.c_int),
                    ("sensor_name", ctypes.c_char * 64),
                    ("serial_number", ctypes.c_char * 64)]    


class PicamAvailableData(ctypes.Structure):
    _fields_ = [("initial_readout", ctypes.c_void_p),
                ("readout_count", ctypes.c_int64)]


class PicamAcquisitionStatus(ctypes.Structure):
    _fields_ = [("running", ctypes.c_bool),
                ("errors", ctypes.c_int),
                ("readout_rate", ctypes.c_double)]

class PicamRoi(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int),
                ("width", ctypes.c_int),
                ("x_binning", ctypes.c_int),
                ("y", ctypes.c_int),
                ("height", ctypes.c_int),
                ("y_binning", ctypes.c_int)]


class PicamRois(ctypes.Structure):
    _fields_ = [("roi_array", ctypes.POINTER(PicamRoi)),
                ("roi_count", ctypes.c_int)]
                    
class Camera():
    def __init__(self,*,libPath: str='C:/Users/UPX/Desktop/python/PICam/Picam.dll'):#C:/Program Files/Princeton Instruments/PICam/Runtime/Picam.dll'):	#class will instantiate and initialize PICam
        self.cam = ctypes.c_void_p(0)
        self.dev = ctypes.c_void_p(0)
        self.camID = camIDStruct(0,0,b'',b'')
        self.camIDs = None
        self.numRows = ctypes.c_int(0)
        self.numCols = ctypes.c_int(0)
        self.readRate = ctypes.c_double(0)
        #pathToLib = os.path.join(os.environ["PicamRoot"], "Runtime")
        #pathToLib = os.path.join(pathToLib, "Picam.dll")
        #print( 'dll file: ',pathToLib)
        pathToLib = 'C:\Program Files\Common Files\Princeton Instruments\Picam\Runtime\picam.dll'
        self.picamLib = ctypes.CDLL(pathToLib, winmode=0)   #cdll.LoadLibrary(pathToLib) # add winmode see :https://syntaxbug.com/ea75a69575/
        self.counter = 0
        self.totalData = np.array([])
        self.newestFrame = np.array([])
        self.rStride = ctypes.c_int(0)
        self.display = False
        self.runningStatus = ctypes.c_bool(False)
        self.windowName = ''
        self.circBuff = circBuff = ctypes.ARRAY(ctypes.c_ubyte,0)()
        self.aBuf = acqBuf(0,0)
        self.Initialize()

    def AcquisitionUpdated(self, device, available, status):    #PICam will launch callback in another thread
        with lock:
            if status.contents.running:
                self.ProcessData(available.contents, self.rStride.value, saveAll = False)					
                self.runningStatus = status.contents.running
        return 0
        
    def ResetCount(self):
        self.counter = 0
        self.totalData = np.array([])

    def GetReadRate(self):
        self.picamLib.Picam_GetParameterFloatingPointValue(self.cam,paramReadRate,ctypes.byref(self.readRate))

    def Initialize(self):
        initCheck = ctypes.c_bool(0)
        self.picamLib.Picam_InitializeLibrary()
        self.picamLib.Picam_IsLibraryInitialized(ctypes.byref(initCheck))
        
        if initCheck:
			#version check if PICam successfully initialized
            major = ctypes.c_int(0)
            minor = ctypes.c_int(0)
            distribution = ctypes.c_int(0)
            released = ctypes.c_int(0)
            self.picamLib.Picam_GetVersion(ctypes.byref(major),ctypes.byref(minor),ctypes.byref(distribution),ctypes.byref(released))
            print('PICam Initialized: %r'%initCheck.value)
            print("\tVersion Picam dll  %d.%d.%d.%d"%(major.value, minor.value, distribution.value, released.value))

    def Uninitialize(self):
        self.picamLib.Picam_UninitializeLibrary()

    def GetFirstROI(self):		#working with single ROI for basic demonstration
        rois = ctypes.c_void_p(0)		
        self.picamLib.Picam_GetParameterRoisValue(self.cam, paramROIs, ctypes.byref(rois))
        roisCast = ctypes.cast(rois,ctypes.POINTER(roisStruct))[0]
        roiCast = ctypes.cast(roisCast.roi_array,ctypes.POINTER(roiStruct))[0]	#take first ROI
        self.numCols = int(roiCast.width/roiCast.x_binning)
        self.numRows = int(roiCast.height/roiCast.y_binning)
        self.picamLib.Picam_DestroyRois(rois)
        self.w = self.getParameter("PicamParameter_ActiveWidth")
        self.h = self.getParameter("PicamParameter_ActiveHeight")
        self.totalFrameSize = self.w * self.h
        

    def Commit(self,*,printMessage: bool=True):
        paramArray = ctypes.pointer(ctypes.c_int(0))
        failedCount = ctypes.c_int(1)
        self.picamLib.Picam_CommitParameters(self.cam, ctypes.byref(paramArray), ctypes.byref(failedCount))
        if failedCount.value > 0:
            print('Failed to commit %d parameters. Cannot acquire.'%(failedCount.value))
            return False
        else:
            self.GetReadRate()
            if printMessage:
                pass
                #print('\tCommit successful! Current readout rate: %0.2f readouts/sec'%(self.readRate.value))
            return True

    def OpenFirstCamera(self):#,*,model: int=57): #if a connected camera is found, opens the first one, otherwise opens a demo		
        
        if self.picamLib.Picam_OpenFirstCamera(ctypes.byref(self.cam)) > 0:
            self.picamLib.Picam_ConnectDemoCamera(57,b'SLTest',ctypes.byref(self.camID))
            if self.picamLib.Picam_OpenCamera(ctypes.byref(self.camID),ctypes.byref(self.cam)) > 0:
                print('No camera could be opened. Uninitializing.')
                self.Uninitialize()
                self.oneCameraConnected=False
                return self.oneCameraConnected
            else:
                self.picamLib.Picam_GetCameraID(self.cam,ctypes.byref(self.camID))
        else:
            self.picamLib.Picam_GetCameraID(self.cam,ctypes.byref(self.camID))
            print('Open First camera avaible : Camera Sensor: %s, Serial #: %s'%(self.camID.sensor_name.decode('utf-8'),self.camID.serial_number.decode('utf-8')))
        #self.GetFirstROI() # modif 2025/02 for quadro 
        
        #print('\tFirst ROI: %d (cols) x %d (rows)'%(self.numCols,self.numRows))
    
        
   
         
    def OpenCamerabySerial(self,serial=0):

        if serial==0 or serial==None:
             
             self.OpenFirstCamera()
        else :
            self.camIDs = ctypes.pointer(PicamCameraID())
            id_count = ctypes.c_int()
            self.picamLib.Picam_GetAvailableCameraIDs(ctypes.byref(self.camIDs),ctypes.pointer(id_count))
            serialNumber=[]
            sensorName=[]
            modele=[]
            self.oneCameraConnected=False
            for i in range(id_count.value): # à supprimer si la camera est une MTE ?
                modele.append(self.camIDs[i].model) # picam.h for model 
                sensorName.append(self.camIDs[i].sensor_name.decode('utf-8'))
                serialNumber.append(self.camIDs[i].serial_number.decode('utf-8'))
                if serial==self.camIDs[i].serial_number.decode('utf-8'):
                    self.camID=self.camIDs[i]
                    if self.picamLib.Picam_OpenCamera(ctypes.byref(self.camID),ctypes.byref(self.cam)) > 0:
                        print('No camera could be opened.')
                        self.oneCameraConnected=False
                    else :
                        print('camera s/n:',self.camIDs[i].serial_number.decode('utf-8'),'sensor :', self.camIDs[i].sensor_name.decode('utf-8'),'connected ')                    
                        self.oneCameraConnected=True
                        self.GetFirstROI()
                    
            print(id_count.value,' camera (s)  available:',sensorName,serialNumber)
            if self.oneCameraConnected==False:
               self.oneCameraConnected=self.OpenFirstCamera()
            return self.oneCameraConnected
            
        
    def getSerialNumber(self):
         return self.camID.serial_number.decode('utf-8')    
        
    def getAvailableCameras(self):
        if self.camIDs is not None and not isinstance(self.camIDs, list):
            self.picamLib.Picam_DestroyCameraIDs(self.camIDs)
            self.camIDs = None
        # get connected cameras
        self.camIDs = ctypes.pointer(PicamCameraID())
        id_count = ctypes.c_int()
        self.picamLib.Picam_GetAvailableCameraIDs(ctypes.byref(self.camIDs),ctypes.pointer(id_count))
        #print(id_count.value,self.camIDs)
        serialNumber=[]
        sensorName=[]
        modele=[]
        for i in range(id_count.value): # à supprimer si la camera est une MTE
#                print('  Model is ', pit.PicamModelLookup[self.camIDs[i].model])
                modele.append(self.camIDs[i].model) # picam.h for model 
                sensorName.append(self.camIDs[i].sensor_name.decode('utf-8'))
                serialNumber.append(self.camIDs[i].serial_number.decode('utf-8'))
        return(modele,sensorName,serialNumber)
        
    def SetExposure(self, value):
        self.setParameter("PicamParameter_ExposureTime",value)
        # print("exposure set to :",self.GetExposure())
    def GetExposure(self):
        exp=self.getParameter("PicamParameter_ExposureTime")
        # print("Exposure  is :",exp)
        return exp
    
    def setParameter(self, name, value):
        prm =PicamParameter[name]
        
        exists = ctypes.c_bool()
        self.picamLib.Picam_DoesParameterExist(self.cam, prm, ctypes.pointer(exists))
        if not exists:
            print("Ignoring parameter", name)
            print("  Parameter does not exist for current camera!")
            return
    
        access = ctypes.c_int()
        self.picamLib.Picam_GetParameterValueAccess(self.cam, prm, ctypes.pointer(access))
        if PicamValueAccessLookup[access.value] not in ["ReadWrite", "ReadWriteTrivial"]:
            print("Ignoring parameter", name)
            print("  Not allowed to overwrite parameter!")
            return
        if PicamValueAccessLookup[access.value] == "ReadWriteTrivial":
            print("WARNING: Parameter", name, " allows only one value!")
    
        # get type of parameter
        type = ctypes.c_int()
        self.picamLib.Picam_GetParameterValueType(self.cam, prm, ctypes.pointer(type))

        if type.value not in PicamValueTypeLookup:
            print("Ignoring parameter", name)
            print("  Not a valid parameter type:", type.value)
            return

        if PicamValueTypeLookup[type.value] in ["Integer", "Boolean", "Enumeration"]:
            val = ctypes.c_int(value)
            self.picamLib.Picam_SetParameterIntegerValue(self.cam, prm, val)

        if PicamValueTypeLookup[type.value] == "LargeInteger":
            val = ctypes.c_int64(value)
            self.picamLib.Picam_SetParameterLargeIntegerValue(self.cam, prm, val)

        if PicamValueTypeLookup[type.value] == "FloatingPoint":
            val = ctypes.c_double(value)
            self.picamLib.Picam_SetParameterFloatingPointValue(self.cam, prm, val)

        if PicamValueTypeLookup[type.value] == "Rois":
            self.picamLib.Picam_SetParameterRoisValue(self.cam, prm, ctypes.pointer(value))

        if PicamValueTypeLookup[type.value] == "Pulse":
            self.picamLib.Picam_SetParameterPulseValue(self.cam, prm, ctypes.pointer(value))

        if PicamValueTypeLookup[type.value] == "Modulations":
            self.picamLib.Picam_SetParameterModulationsValue(self.cam, prm, ctypes.pointer(value))
        self.Commit(printMessage=True)
        
        
        
    def getParameter(self, name):
        prm = PicamParameter[name]
        exists = ctypes.c_bool()
        self.picamLib.Picam_DoesParameterExist(self.cam, prm, ctypes.pointer(exists))
    
        # get type of parameter
        type = ctypes.c_int()
        self.picamLib.Picam_GetParameterValueType(self.cam, prm, ctypes.pointer(type))
    
        if PicamValueTypeLookup[type.value] in ["Integer", "Boolean", "Enumeration"]:
            val = ctypes.c_int()
    
            # test whether we can read the value directly from hardware
            cr = ctypes.c_int()
            self.picamLib.Picam_CanReadParameter(self.cam, prm, ctypes.pointer(cr))
            if cr.value:
                if self.picamLib.Picam_ReadParameterIntegerValue(self.cam, prm, ctypes.pointer(val)) == 0:
                    return val.value
            else:
                if self.picamLib.Picam_GetParameterIntegerValue(self.cam, prm, ctypes.pointer(val)) == 0:
                    return val.value
    
        if PicamValueTypeLookup[type.value] == "LargeInteger":
            val = ctypes.c_int64()
            if self.picamLib.Picam_GetParameterLargeIntegerValue(self.cam, prm, ctypes.pointer(val)) == 0:
                return val.value
    
        if PicamValueTypeLookup[type.value] == "FloatingPoint":
            val = ctypes.c_double()
    
            # NEW
            # test whether we can read the value directly from hardware
            cr = ctypes.c_bool()
            self.picamLib.Picam_CanReadParameter(self.cam, prm, ctypes.pointer(cr))
            if cr.value:
                if self.picamLib.Picam_ReadParameterFloatingPointValue(self.cam, prm, ctypes.pointer(val)) == 0:
                    return val.value
            else:
                if self.picamLib.Picam_GetParameterFloatingPointValue(self.cam, prm, ctypes.pointer(val)) == 0:
                    return val.value
    
        if PicamValueTypeLookup[type.value] == "Rois":
            val = roiStruct()
            if self.picamLib.Picam_GetParameterRoisValue(self.cam, prm, ctypes.pointer(val)) == 0:
                self.roisPtr.append(val)
                return val.contents
    
        if PicamValueTypeLookup[type.value] == "Pulse":
            val = ctypes.pointer(PicamPulse())
            if self.picamLib.Picam_GetParameterPulseValue(self.cam, prm, ctypes.pointer(val)) == 0:
                self.pulsePtr.append(val)
                return val.contents
    
        if PicamValueTypeLookup[type.value] == "Modulations":
            val = ctypes.pointer(PicamModulations())
            if self.picamLib.Picam_GetParameterModulationsValue(self.cam, prm, ctypes.pointer(val)) == 0:
                self.modPtr.append(val)
                return val.contents

        return None 
    
    def Acquisition(self, N=1, timeout=100000):
        
        # print('Acquire')
        self.available = PicamAvailableData()
        errors = ctypes.c_int()
        running = ctypes.c_bool()
        self.picamLib.Picam_IsAcquisitionRunning(self.cam, ctypes.pointer(running))
        #print('running value',running.value)
        if running.value:
            print("ERROR: acquisition still running")
            return []
        t = time.time()
        self.picamLib.Picam_Acquire(self.cam, ctypes.c_int64(N), ctypes.c_int(timeout), ctypes.pointer(self.available), ctypes.pointer(errors))
        #(cameraHandel,readoutcount,readouttimeout,outpoutParameter=avaible,outpouterrors)
        # print('available',self.available)
        print("Durée de l'acquisition : %f s" % (time.time() - t) )
#        print(errors)
        return t
    
    def IsAcquisitionRunning(self):
        running = ctypes.c_bool()
        self.picamLib.Picam_IsAcquisitionRunning(self.cam, ctypes.pointer(running))
#        print('isRunning')
#        print(running.value)
        return running.value
    
    def StopAcquisition(self):
        self.picamLib.Picam_StopAcquisition(self.cam)
    
    def GetAcquiredData(self):
        """This is an internally used function to convert the readout buffer into a sequence of numpy arrays.
        It reads all available data at once into a numpy buffer and reformats data to a usable format.

        :param long address: Memory address where the readout buffer is stored.
        :param int size: Number of readouts available in the readout buffer.
        :returns: List of ROIS; for each ROI, array of readouts; each readout is a NxM array.
        """
       
        dataArrayType = ctypes.c_uint16 * int(self.totalFrameSize) #readoutstride
        dataArrayPointerType = ctypes.POINTER(dataArrayType)
        dataPointer = ctypes.cast(self.available.initial_readout, dataArrayPointerType)

        # create a numpy array from the buffer
        data = np.frombuffer(dataPointer.contents, dtype=np.uint16)
        return np.array(data).reshape((int(self.h), int(self.w)))


    def GetTemperature(self):
        self.temperature = self.getParameter("PicamParameter_SensorTemperatureReading")
        return self.temperature

    def SetTemperature(self, temperature):
        a = self.setParameter("PicamParameter_SensorTemperatureSetPoint", int(temperature))
        #print('temp set',a)
        
    def GetTemperatureStatus(self):
        return self.getParameter("PicamParameter_SensorTemperatureStatus")
        
    def GetShutterControl(self,shutter):
        """
        if shutter control set to true signal will available at the output
        """
        return self.getParameter("PicamParameter_ShutterControl")
        
    
    def SetShutterControl(self,shutter):
        """
        if shutter control set to true signal will available at the output
        """
        self.setParameter("PicamParameter_ShutterControl",int(shutter))
        
    def SetAdcConf(self, gain=3, speed=1.0):
        # gain High, Medium ou Low; plutot High   "Low": 1,
        #"Medium": 2,
        #"High": 3""
        # speed 0.5 ou 1.0; plutot 1.0
        self.setParameter("PicamParameter_AdcAnalogGain", gain)
        self.setParameter("PicamParameter_AdcSpeed", speed) # 0.5 ou 1.0    
    
    
    
    def setROI(self, x0, w, xbin, y0, h, ybin, store):
        """Create a single region of interest (ROI).

        :param int x0: X-coordinate of upper left corner of ROI.
        :param int w: Width of ROI.
        :param int xbin: X-Binning, i.e. number of columns that are combined into one larger column (1 to w).
        :param int y0: Y-coordinate of upper left corner of ROI.
        :param int h: Height of ROI.
        :param int ybin: Y-Binning, i.e. number of rows that are combined into one larger row (1 to h).
        """
        r = PicamRoi(x0, w, xbin, y0, h, ybin)
        R = PicamRois(ctypes.pointer(r), store)   # change 1 to 0 to remove a bug ?!? store the number of region 
        self.setParameter("PicamParameter_Rois", R)
        self.setParameter("PicamParameter_Rois", R)
        self.totalFrameSize =( (w / xbin) * (h / ybin))
        self.w = (w/xbin) # modif self.w=w
        self.h = (h/ybin)
    
    
    def disconnect(self):
        """Disconnect current camera.
        """
        if self.cam is not None:
            self.picamLib.Picam_CloseCamera(self.cam)
        self.cam = None
        self.picamLib.Picam_UninitializeLibrary()
    
    
# 	def ProcessData(self, data, readStride,*,saveAll: bool=True):
# 		x=ctypes.cast(data.initial_readout,ctypes.POINTER(ctypes.c_uint16))
# 		for i in range(0,data.readout_count):	#readout by readout
# 			offset = int((i * readStride) / 2)
# 			readoutDat = np.asarray(x[offset:int(self.numCols*self.numRows + offset)],dtype=np.uint16)
# 			readoutDat = np.reshape(readoutDat, (self.numRows, self.numCols))
# 			if saveAll:
# 				self.totalData[(self.counter),:,:] = readoutDat
# 			self.counter += 1
# 			if i == data.readout_count-1:	#return most recent readout (normalized) to use for displaying
# 				self.newestFrame = readoutDat

# 	def AcquireHelper(self):
# 		dat = availableData(0,0)
# 		aStatus=acqStatus(False,0,0)
# 		self.picamLib.Picam_StartAcquisition(self.cam)
# 		print('Acquisition Started, %0.2f readouts/sec...'%self.readRate.value)
# 		#start a do-while
# 		self.picamLib.Picam_WaitForAcquisitionUpdate(self.cam,-1,ctypes.byref(dat),ctypes.byref(aStatus))
# 		self.ProcessData(dat, self.rStride.value)
# 		#while part
# 		while(aStatus.running):
# 			self.picamLib.Picam_WaitForAcquisitionUpdate(self.cam,-1,ctypes.byref(dat),ctypes.byref(aStatus))
# 			self.runningStatus = aStatus.running
# 			if dat.readout_count > 0:					
# 				self.ProcessData(dat, self.rStride.value)
# 		#print('...Acquisiton Finished, %d readouts processed.'%(self.counter)) #is not needed since the DisplayCameraData function prints as well

# 	def Acquire(self,*,frames: int=1):	#will launch the AcquireHelper function in a new thread when user calls it
# 		frameCount = ctypes.c_int(0)
# 		frameCount.value = frames
# 		self.picamLib.Picam_SetParameterLargeIntegerValue(self.cam,paramFrames,frameCount)
# 		if self.Commit():
# 			self.ResetCount()
# 			self.totalData = np.zeros((frameCount.value,self.numRows,self.numCols))
# 			if self.display:
# 				SetupDisplay(self.numRows, self.numCols, self.windowName)
# 			self.picamLib.Picam_GetParameterIntegerValue(self.cam, paramStride, ctypes.byref(self.rStride))			
# 			acqThread = threading.Thread(target=self.AcquireHelper)
# 			acqThread.start()	#data processing will be in a different thread than the display

# 	def DisplayCameraData(self):	#this will block and then unregister callback (if applicable) when done
# 		#do-while
# # 		cv2.waitKey(100)
# 		runStatus = ctypes.c_bool(False)
# 		self.picamLib.Picam_IsAcquisitionRunning(self.cam, ctypes.byref(runStatus))
# 		self.runningStatus = runStatus
# 		while self.runningStatus:
# 			if self.display and len(self.newestFrame) > 0:									
# 				DisplayImage(self.newestFrame, self.windowName)
# 		print('Acquisition stopped. %d readouts obtained.'%(self.counter))
# 		try:
# 			self.picamLib.PicamAdvanced_UnregisterForAcquisitionUpdated(self.dev, self.acqCallback)
# 		except:
# 			pass
# # 		cv2.waitKey(20000)
# # 		cv2.destroyAllWindows()

    
# 	def AcquireCB(self,*,frames: int=5):	#utilizes Advanced API to demonstrate callbacks, returns immediately
# 		if self.display:
# 			SetupDisplay(self.numRows, self.numCols, self.windowName)
# 		self.ResetCount()
# 		self.picamLib.Picam_GetParameterIntegerValue(self.cam, paramStride, ctypes.byref(self.rStride))		
# 		self.picamLib.PicamAdvanced_GetCameraDevice(self.cam, ctypes.byref(self.dev))
# 		frameCount = ctypes.c_int(0)
# 		frameCount.value = frames
# 		self.picamLib.Picam_SetParameterLargeIntegerValue(self.dev,paramFrames,frameCount)	#setting with dev handle commits to physical device if successful
# 		#circ buffer so we can run for a long time without needing to allocate memory for all of it
# 		#the buffer array and the data structure should be global or class properties so they remain in scope when the
# 		#function returns		
# 		widthNominal = np.floor(512*1024*1024/self.rStride.value)
# 		if widthNominal < 4:					#if 512MB not enough for 4 frames, allocate for 4 frames
# 			buffWidth = self.rStride.value*4
# 		else:
# 			buffWidth = int(widthNominal)*self.rStride.value
# 		self.circBuff = ctypes.ARRAY(ctypes.c_ubyte,buffWidth)()
# 		self.aBuf.memory = ctypes.addressof(self.circBuff)
# 		self.aBuf.memory_size = ctypes.c_longlong(buffWidth)
# 		self.picamLib.PicamAdvanced_SetAcquisitionBuffer(self.dev, ctypes.byref(self.aBuf))
# 		
# 		CMPFUNC = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(availableData), ctypes.POINTER(acqStatus))
# 		#lines for internal callback		
# 		self.acqCallback = CMPFUNC(self.AcquisitionUpdated)
# 		self.picamLib.PicamAdvanced_RegisterForAcquisitionUpdated(self.dev, self.acqCallback)
# 		self.picamLib.Picam_StartAcquisition(self.dev)		
# 		print('Acquisition of %d frames asynchronously started'%(frameCount.value))

# 	def ReturnData(self):
# 		return self.totalData

    def Close(self):
        self.picamLib.Picam_CloseCamera(self.cam)
        self.picamLib.Picam_DisconnectDemoCamera(ctypes.byref(self.camID))
        self.Uninitialize()
