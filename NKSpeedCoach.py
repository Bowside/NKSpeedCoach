import pandas
from io import StringIO

class NKSession(object):
    def __init__(self, NKSessionFile):

        NKSessionFile.pseudofile.seek(0)
        self._getnksessionheader(NKSessionFile.pseudofile)
        NKSessionFile.pseudofile.seek(0)
        self._getsessionsummary(NKSessionFile.pseudofile, NKSessionFile.sessionsummarystart, NKSessionFile.sessionintervalsummarystart)
        NKSessionFile.pseudofile.seek(0)
        self._getsessionintervalsummaries(NKSessionFile.pseudofile, NKSessionFile.sessionintervalsummarystart, NKSessionFile.perstrokedatastart)
        NKSessionFile.pseudofile.seek(0)
        self._getsessionstrokedata(NKSessionFile.pseudofile, NKSessionFile.perstrokedatastart)

    def _getnksessionheader(self, pseudofile):

        #Read CSV file where session header resides
        SessionHeaderDF = pandas.read_csv(pseudofile, header=None, skiprows = 2, nrows=5, usecols=[0,1], names=["Field", "Value"])
        #strip Whitspace
        SessionHeaderDF = SessionHeaderDF.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        self.SessionName = SessionHeaderDF.iloc[0,1]
        self.SessionStartTime = SessionHeaderDF.iloc[1,1]
        self.SessionType = SessionHeaderDF.iloc[2,1]
        self.SessionSystemOfUnits = SessionHeaderDF.iloc[3,1]
        self.SessionSpeedInput = SessionHeaderDF.iloc[4,1]

    def _getsessionsummary(self, pseudofile, sessionsummarystart, sessionintervalsummarystart):
        
        #Read session summary into dataframe
        rowrange = sessionintervalsummarystart - sessionsummarystart - 5
        SessionSummaryDF = pandas.read_csv(pseudofile, header=0, skiprows = sessionsummarystart, nrows=rowrange, sep=",")    
        #Drop first row
        SessionSummaryDF.drop(SessionSummaryDF.index[0], inplace=True)   
        #Data Fixes
        SessionSummaryDF.replace({"---": None}, inplace = True)
        SessionSummaryDF.replace(":60.0", ":59.9", inplace = True, regex=True)
        self.SessionSummary = SessionSummaryDF

    def _getsessionintervalsummaries(self, pseudofile, sessionintervalsummarystart, perstrokedatastart):
        
        #Read session interval summaries into dataframe
        rowrange = perstrokedatastart - sessionintervalsummarystart - 6
        SessionIntervalSummariesDF = pandas.read_csv(pseudofile, header=0, skiprows = sessionintervalsummarystart, nrows=rowrange, sep=",")    
        #Drop first row
        SessionIntervalSummariesDF.drop(SessionIntervalSummariesDF.index[0], inplace=True)   
        #Data Fixes
        SessionIntervalSummariesDF.replace({"---": None}, inplace = True)
        SessionIntervalSummariesDF.replace(":60.0", ":59.9", inplace = True, regex=True)
        self.SessionIntervalSummaries = SessionIntervalSummariesDF

    def _getsessionstrokedata(self, pseudofile, perstrokedatastart):

        #Read session details into dataframe
        SessionStrokeDataDF = pandas.read_csv(pseudofile, header=0, skiprows = perstrokedatastart , sep=",")    
        #Drop first row
        SessionStrokeDataDF.drop(SessionStrokeDataDF.index[0], inplace=True)   
        #Data Fixes
        SessionStrokeDataDF.replace({"---": None}, inplace = True)
        SessionStrokeDataDF.replace(":60.0", ":59.9", inplace = True, regex=True)
        self.SessionStrokeData = SessionStrokeDataDF

class NKDevice(object):
    def __init__(self, NKSessionFile):

        NKSessionFile.pseudofile.seek(0)
        self._getnkspeedcoachinfo(NKSessionFile.pseudofile)
        NKSessionFile.pseudofile.seek(0)
        self._getnkoarlockinfo(NKSessionFile.pseudofile)
        NKSessionFile.pseudofile.seek(0)
        self._getnkoarlocksettings(NKSessionFile.pseudofile)
        
    def _getnkspeedcoachinfo(self, pseudofile):

        #Read CSV file where device information resides
        DeviceDF = pandas.read_csv(pseudofile, header=None, skiprows=2, nrows=6, usecols=[4,5] , names=["Field", "Value"])
        #Strip WhiteSpace
        DeviceDF = DeviceDF.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        self.DeviceName = DeviceDF.iloc[0,1]
        self.DeviceModel = DeviceDF.iloc[1,1]
        self.DeviceSerial = DeviceDF.iloc[2,1]
        self.DeviceFirmwareVersion = DeviceDF.iloc[3,1]
        self.DeviceProfileVersion = DeviceDF.iloc[4,1]
        self.DeviceHardwareVersion = DeviceDF.iloc[5,1]

    def _getnkoarlockinfo(self, pseudofile):

        #Read CSV file where oarlock firmware data resides
        OarlockFirmwareDF = pandas.read_csv(pseudofile, header=None, skiprows=2, nrows=1, usecols=[8,9], names=["Field", "Value"])
        #Strip WhiteSpace
        OarlockFirmwareDF = OarlockFirmwareDF.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        self.DeviceOarlockFirmwareVersion = OarlockFirmwareDF.iloc[0,1]

    def _getnkoarlocksettings(self, pseudofile):

        #Read CSV file where oarlock metadata resides
        OarlockMetaDataDF = pandas.read_csv(pseudofile, header=None, skiprows = 2, nrows=5, usecols=[12,13], names=["Field", "Value"])
        #Strip WhiteSpace
        OarlockMetaDataDF = OarlockMetaDataDF.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        
        self.DeviceOarlockBoatId = OarlockMetaDataDF.iloc[0,1]
        self.DeviceOarlockSeatNumber = OarlockMetaDataDF.iloc[1,1]
        self.DeviceOarlockSide = OarlockMetaDataDF.iloc[2,1]
        self.DeviceOarlockOarlLength = OarlockMetaDataDF.iloc[3,1]
        self.DeviceOarlockInboardLength = OarlockMetaDataDF.iloc[4,1]

class NKSessionFile(object):

    init = False

    def __init__(self, filepath):
        if self.init is False:
            self._createpseudofile(filepath)
  
    def _createpseudofile(self, filepath):
        
        #Open the file
        nkfile = open(filepath, "r")
        
        #Read the file and determine the data start points
        i = 1
        for line in nkfile.readlines():
            if "Session Summary:" in line:
                self.sessionsummarystart = i
            elif "Interval Summaries:" in line:
                self.sessionintervalsummarystart = i
            elif "Per-Stroke Data:" in line:
                self.perstrokedatastart = i
            i += 1

        #Very basic check to see if its a valid file
        if self.sessionsummarystart == 0 and self.sessionintervalsummarystart == 0 and self.perstrokedatastart == 0:
            print(f'File {filepath} does not appear to be a valid NK Speedcoach file!')
        else:
            nkfile.seek(0)
            self.pseudofile = StringIO(nkfile.read())
            self.init = True
