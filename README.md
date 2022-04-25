# syslogcef

Python library to easily send CEF formatted messages to syslog server. 

It uses [cefevent](https://pypi.org/project/cefevent/) to format message payloads and [rfc5424-logging-handler](https://pypi.org/project/rfc5424-logging-handler/) to send syslogs.

Install:

```bash
pip install syslogcef
```

Usage:

```python
from syslogcef import SyslogCEFSender

syslog = SyslogCEFSender('10.1.2.3', '514', 'TCP', deviceProduct='MyProgram', deviceVersion='1.0.2')
syslog.register_event('100', 'CPU temp is OK', 0)
syslog.register_event('101', 'CPU temp is rising', 5)
syslog.register_event('102', 'CPU temp is too high', 9, reason="Exceeds 70 degres celsius")

syslog.send('102', message="The CPU temp is 88 degres celsius.", sourceHostName="mydevice.mydomain.com", sourceMacAddress="00:00:ee:00:52:bb")
```

See [cefevent](https://github.com/kamushadenes/cefevent/blob/master/cefevent/extensions.py) for complete list of fields. 
