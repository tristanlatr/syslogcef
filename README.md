# syslogcef

Python library to easily send CEF formatted messages to syslog server. 

It uses [cefevent](https://pypi.org/project/cefevent/) to format message payloads and [rfc5424-logging-handler](https://pypi.org/project/rfc5424-logging-handler/) to send syslogs.

Install:

```bash
pip install syslogcef
```

Test sending a few messages with:

```bash
python3 -m syslogcef.testmessages --host <host> --port <port> --proto [TCP|UDP]
```

Usage:

```python
from syslogcef import SyslogCEFSender

# Create syslog sender.
syslog = SyslogCEFSender(
    # Syslog server settings:
    host='10.1.2.3', 
    port='514', 
    protocol='TCP', 
    # Hopefully the above names does not clash with any CEF field name.
    # CEF fields applied to all events:
    deviceProduct='MyProgram', 
    deviceVendor='MyCompany',
    deviceVersion='1.0.2')

# Register CEF events.
syslog.register_event('100', name='CPU temp is OK', severity=0)
syslog.register_event('101', name='CPU temp is rising', severity=5)
syslog.register_event('102', name='CPU temp is too high', severity=9, 
    # CEF fields applied to all '102' events:
    reason="Exceeds 70 degres celsius")

# Send one syslog message.
syslog.send('102', message="The CPU temp is 88 degres celsius.", 
    # CEF fields applied only to this event:
    sourceHostName="mydevice.mydomain.com", 
    sourceMacAddress="00:00:ee:00:52:bb")
```

See [cefevent](https://github.com/kamushadenes/cefevent/blob/master/cefevent/extensions.py) for complete list of fields. 

Read the full [ArcSight CEF format](https://docs.centrify.com/Content/IntegrationContent/SIEM/arcsight-cef/arcsight-cef-format.htm) for more informations.
