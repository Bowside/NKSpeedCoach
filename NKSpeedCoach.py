"""
Create a representation of the NK speedCoach data file.

Classes:
    NKSession
    NKDevice
    NKSessionFile

Functions:
    None

Misc variables:
    None
"""

import pandas
from io import StringIO


class NKSession(object):
    """
    A class to containing the session data obtained from a single NK SpeedCoach File.

    Attributes:
        sessionname : str
            The name of the session
        sessionspeedinput : str
            The source of the speed data, (GPS; Impeller)
        sessionstarttime : str
            The time that the session was started
        sessionsystemofunits : str
            The system of units the sessions was captured in (M M/S /500m; KM KMH /500m; MI MPH /MI)
        sessiontype : str
            The type of session (Just Row; Intervals)
        sessionsummary : dataframe[]
            A dataframe representing a single row denoting a sessions summary
        sessionintervalsummaries : dataframe[]
            A dataframe containing a summary row for each interval that was done during the session
        sessionstrokedata : dataframe[]
            A datafream containing a row for each stroke take for all summaries

    """

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

        # Read CSV file where session header resides
        SessionHeaderDF = pandas.read_csv(pseudofile, header=None, skiprows=2, nrows=5, usecols=[0, 1], names=["Field", "Value"])
        # Strip Whitspace
        SessionHeaderDF = SessionHeaderDF.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        self.SessionName = SessionHeaderDF.iloc[0, 1]
        self.SessionStartTime = SessionHeaderDF.iloc[1, 1]
        self.SessionType = SessionHeaderDF.iloc[2, 1]
        self.SessionSystemOfUnits = SessionHeaderDF.iloc[3, 1]
        self.SessionSpeedInput = SessionHeaderDF.iloc[4, 1]

    def _getsessionsummary(self, pseudofile, sessionsummarystart, sessionintervalsummarystart):

        # Read session summary into dataframe
        rowrange = sessionintervalsummarystart - sessionsummarystart - 5
        SessionSummaryDF = pandas.read_csv(pseudofile, header=0, skiprows=sessionsummarystart, nrows=rowrange, sep=",")
        # Drop first row
        SessionSummaryDF.drop(SessionSummaryDF.index[0], inplace=True)
        # Data Fixes
        SessionSummaryDF.replace({"---": None}, inplace=True)
        SessionSummaryDF.replace(":60.0", ":59.9", inplace=True, regex=True)
        self.SessionSummary = SessionSummaryDF

    def _getsessionintervalsummaries(self, pseudofile, sessionintervalsummarystart, perstrokedatastart):

        # Read session interval summaries into dataframe
        rowrange = perstrokedatastart - sessionintervalsummarystart - 6
        SessionIntervalSummariesDF = pandas.read_csv(pseudofile, header=0, skiprows=sessionintervalsummarystart, nrows=rowrange, sep=",")
        # Drop first row
        SessionIntervalSummariesDF.drop(SessionIntervalSummariesDF.index[0], inplace=True)
        # Data Fixes
        SessionIntervalSummariesDF.replace({"---": None}, inplace=True)
        SessionIntervalSummariesDF.replace(":60.0", ":59.9", inplace=True, regex=True)
        self.SessionIntervalSummaries = SessionIntervalSummariesDF

    def _getsessionstrokedata(self, pseudofile, perstrokedatastart):

        # Read session details into dataframe
        SessionStrokeDataDF = pandas.read_csv(pseudofile, header=0, skiprows=perstrokedatastart, sep=",")
        # Drop first row
        SessionStrokeDataDF.drop(SessionStrokeDataDF.index[0], inplace=True)
        # Data Fixes
        SessionStrokeDataDF.replace({"---": None}, inplace=True)
        SessionStrokeDataDF.replace(":60.0", ":59.9", inplace=True, regex=True)
        self.SessionStrokeData = SessionStrokeDataDF


class NKDevice(object):
    """
    A class to containing the device information obtained from a single NK SpeedCoach File.

    Attributes:
        devicefirmwareversion : str
            The firmware version of the speedcoach device
        devicehardwareversion : str
            The hardware version of the speedcoach device
        devicemodel : str
            The model of the speedcoach device
        devicename : str
            The name of the speedcoach device
        deviceprofileversion : str
            The profile version of the speedcoach device
        deviceprofileversion : str
            The serial number of the speedcoach device
            These are unique across devices and can be used as a key
        deviceoarlockboatid : str
            The name assgned to the oarlock device
            Used to identify the boat the device is installed in
        deviceoarlockfirmwareversion : str
            The firmware version of the oarlock device
        deviceoarlockinboardlength : str
            The inboard length of the oar/blade used on the oarlock device
        deviceoarlockinboardlength : str
            The overall length of the oar/blade used on the oarlock device
        deviceoarlockseatnumber : str
            The seat number of the rigger on which the oarlock device is installed
        deviceoarlockside : str
            The side of the rigger on which the oarlock device is installed
    """

    def __init__(self, NKSessionFile):

        NKSessionFile.pseudofile.seek(0)
        self._getnkspeedcoachinfo(NKSessionFile.pseudofile)
        NKSessionFile.pseudofile.seek(0)
        self._getnkoarlockinfo(NKSessionFile.pseudofile)
        NKSessionFile.pseudofile.seek(0)
        self._getnkoarlocksettings(NKSessionFile.pseudofile)

    def _getnkspeedcoachinfo(self, pseudofile):

        # Read CSV file where device information resides
        DeviceDF = pandas.read_csv(pseudofile, header=None, skiprows=2, nrows=6, usecols=[4, 5], names=["Field", "Value"])
        # Strip WhiteSpace
        DeviceDF = DeviceDF.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        self.DeviceName = DeviceDF.iloc[0, 1]
        self.DeviceModel = DeviceDF.iloc[1, 1]
        self.DeviceSerial = DeviceDF.iloc[2, 1]
        self.DeviceFirmwareVersion = DeviceDF.iloc[3, 1]
        self.DeviceProfileVersion = DeviceDF.iloc[4, 1]
        self.DeviceHardwareVersion = DeviceDF.iloc[5, 1]

    def _getnkoarlockinfo(self, pseudofile):

        # Read CSV file where oarlock firmware data resides
        OarlockFirmwareDF = pandas.read_csv(pseudofile, header=None, skiprows=2, nrows=1, usecols=[8, 9], names=["Field", "Value"])
        # Strip WhiteSpace
        OarlockFirmwareDF = OarlockFirmwareDF.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        self.DeviceOarlockFirmwareVersion = OarlockFirmwareDF.iloc[0, 1]

    def _getnkoarlocksettings(self, pseudofile):

        # Read CSV file where oarlock metadata resides
        OarlockMetaDataDF = pandas.read_csv(pseudofile, header=None, skiprows=2, nrows=5, usecols=[12, 13], names=["Field", "Value"])
        # Strip WhiteSpace
        OarlockMetaDataDF = OarlockMetaDataDF.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        self.DeviceOarlockBoatId = OarlockMetaDataDF.iloc[0, 1]
        self.DeviceOarlockSeatNumber = OarlockMetaDataDF.iloc[1, 1]
        self.DeviceOarlockSide = OarlockMetaDataDF.iloc[2, 1]
        self.DeviceOarlockOarlLength = OarlockMetaDataDF.iloc[3, 1]
        self.DeviceOarlockInboardLength = OarlockMetaDataDF.iloc[4, 1]


class NKSessionFile(object):
    """
    A class to represent the NK file.

    When loaded, the file is loaded into an object containing the file contents.
    This object is passed to the other classes.

    The file is parsed to obtain the starting points of various datapoints.
    The starting points are stored within the attributes listed below.

    Attributes
    ----------
    sessionsummarystart : int
        The starting line of the session summary data
    sessionintervalsummarystart : int
        The starting line of the interval summary data
    perstrokedatastart : int
        The starting line of the session stroke data
    pseudofile : string
        An object containing the contents of the NK file

    Methods
    -------
    None

    Returns
    -------
    None
    """

    init = False

    def __init__(self, filepath):
        if self.init is False:
            self._createpseudofile(filepath)

    def _createpseudofile(self, filepath):

        # Open the file
        nkfile = open(filepath, "r")

        # Read the file and determine the data start points
        i = 1
        for line in nkfile.readlines():
            if "Session Summary:" in line:
                self.sessionsummarystart = i
            elif "Interval Summaries:" in line:
                self.sessionintervalsummarystart = i
            elif "Per-Stroke Data:" in line:
                self.perstrokedatastart = i
            i += 1

        # Very basic check to see if its a valid file
        if self.sessionsummarystart == 0 and self.sessionintervalsummarystart == 0 and self.perstrokedatastart == 0:
            print(f'File {filepath} does not appear to be a valid NK Speedcoach file!')
        else:
            nkfile.seek(0)
            self.pseudofile = StringIO(nkfile.read())
            self.init = True
