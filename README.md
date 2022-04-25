# syslogcef
Python library to easily send CEF formatted messages to syslog server

Usage:

```python
from syslogcef import SyslogCEFSender

syslog = SyslogCEFSender('10.1.2.3', '514', 'TCP', deviceProduct='MyProgram')
syslog.register_event('100', 'CPU temp is OK', 0)
syslog.register_event('101', 'CPU temp is rising', 5)
syslog.register_event('102', 'CPU temp is too high', 9)

syslog.send('102', message="The CPU temp is 88 degres celsius.", sourceHostName="mydevice.mydomain.com")
```

See the [ArcSight CEF format](https://docs.centrify.com/Content/IntegrationContent/SIEM/arcsight-cef/arcsight-cef-format.htm#:~:text=The%20Common%20Event%20Format%20\(CEF,formatted%20as%20key%2Dvalue%20pairs) for complete list of fields.
