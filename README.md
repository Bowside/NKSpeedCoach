# NKSpeedCoach
File processing for exports created by the NK SpeedCoach GPS Device

⚠️ This project has been tested with sample files obtained from various speedcoach GPS units using metric data, there are likley file variations that have not been tested. If you have a file that breaks the code, feel free to fix the code or to send me the file!

## Usage

Create an instance of the NK File

```Python 
import NKSpeedCoach
nkfile = r'SpdCoach 2300315 20200107 0805AM.csv'
rowingdata = NKSpeedCoach.NKSessionFile(nkfile)
```

You can then either load an instance of the device details or the session details.

```Python
#Device Class
rowingdevice = NKSpeedCoach.NKDevice(rowingdata)
print(f'Device firmware: {rowingdevice.DeviceFirmwareVersion}')
print(f'Device hardware version: {rowingdevice.DeviceHardwareVersion}')
print(f'Device model: {rowingdevice.DeviceModel}')
print(f'Device name: {rowingdevice.DeviceName}')
print(f'Device profile version: {rowingdevice.DeviceProfileVersion}')
print(f'Device serial: {rowingdevice.DeviceSerial}')
print(f'Device oarlock boat id: {rowingdevice.DeviceOarlockBoatId}')
print(f'Device oarlock firmware version: {rowingdevice.DeviceOarlockFirmwareVersion}')
print(f'Device oarlock inboard length: {rowingdevice.DeviceOarlockInboardLength}')
print(f'Device oarlock oar length: {rowingdevice.DeviceOarlockOarlLength}')
print(f'Device oarlock seat number: {rowingdevice.DeviceOarlockSeatNumber}')
print(f'Device oarlock side: {rowingdevice.DeviceOarlockSide}')

#Session Class
rowingsession = NKSpeedCoach.NKSession(rowingdata)
print(f'Session name: {rowingsession.SessionName}')
print(f'Session speed input: {rowingsession.SessionSpeedInput}')
print(f'Session start time: {rowingsession.SessionStartTime}')
print(f'Session system of units: {rowingsession.SessionSystemOfUnits}')
print(f'Session session type: {rowingsession.SessionType}')
print('Session Summary')
print(rowingsession.SessionSummary)
print('Session Interval Summaries')
print(rowingsession.SessionIntervalSummaries)
print('Session Stroke Data')
print(rowingsession.SessionStrokeData)
```

## Things to note

The NK device sometimes does a very weird thing where data can be stored as 1 minute an 60 seconds.
From what I have managed to work out it is a rounding issue and I round the data down to 1 minute and 59.9 seconds.

