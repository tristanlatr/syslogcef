import typing as t
import pytest

from syslogcef import CEFSender, StdoutSyslogSender, CompositeSyslogSender

if t.TYPE_CHECKING:
    class CapLog(t.Protocol):
        text:str
    
    class CaptureResult(t.Protocol):
        out: str
        err: str

    class CapSys(t.Protocol):
        def readouterr(self) -> CaptureResult: 
            ...
else:
    CapLog = object
    CapSys = object

def test_syslogcef(capsys:CapSys) -> None:

    s = CEFSender(StdoutSyslogSender(), 
        deviceProduct='test-syslogcef', 
        deviceVendor='Github',
        deviceVersion='14.1')

    s.register_event('100', 'Device is reachable', 1)
    s.register_event('101', 'Device is slow to respond', 5)
    s.register_event('102', 'Device is down', 10, reason="Ping failed")

    s.send('100', message='Ping time is: 33ms')
    s.send('101', message='Ping time is: 521ms')
    s.send('102', message='Unreachable')

    assert capsys.readouterr().out == """CEF:0|Github|test-syslogcef|14.1|100|Device is reachable|1|msg=Ping time is: 33ms
CEF:0|Github|test-syslogcef|14.1|101|Device is slow to respond|5|msg=Ping time is: 521ms
CEF:0|Github|test-syslogcef|14.1|102|Device is down|10|reason=Ping failed msg=Unreachable
"""

def test_syslogcef_defaults(capsys:CapSys) -> None:

    s = CEFSender(StdoutSyslogSender(),)

    s.register_event('100', 'Device is reachable', 1)
    s.register_event('101', 'Device is slow to respond', 5)
    s.register_event('102', 'Device is down', 10, reason="Ping failed")

    s.send('100', message='Ping time is: 33ms')
    s.send('101', message='Ping time is: 521ms')
    s.send('102', message='Unreachable')

    assert capsys.readouterr().out == """CEF:0|CEF Vendor|CEF Product|1.0|100|Device is reachable|1|msg=Ping time is: 33ms
CEF:0|CEF Vendor|CEF Product|1.0|101|Device is slow to respond|5|msg=Ping time is: 521ms
CEF:0|CEF Vendor|CEF Product|1.0|102|Device is down|10|reason=Ping failed msg=Unreachable
"""

def test_syslogcef_composite_logger(capsys:CapSys) -> None:
    s = CEFSender(CompositeSyslogSender(StdoutSyslogSender(),StdoutSyslogSender()))
    s.register_event('100', 'Device is reachable', 1)
    s.send('100', message='Ping time is: 33ms')
    assert capsys.readouterr().out == """CEF:0|CEF Vendor|CEF Product|1.0|100|Device is reachable|1|msg=Ping time is: 33ms
CEF:0|CEF Vendor|CEF Product|1.0|100|Device is reachable|1|msg=Ping time is: 33ms
"""

def test_invalid_cef_field() -> None:
    s = CEFSender(StdoutSyslogSender(),)
    with pytest.raises(ValueError):
        s.register_event('100', 'Device is reachable', 1, host='name')
    with pytest.raises(ValueError):
        s.register_event('100', 'Device is reachable', 1, port='port')
    with pytest.raises(ValueError):
        s.register_event('100', 'Device is reachable', 1, port=443)
    with pytest.raises(ValueError):
        s.register_event('100', 'Device is reachable', 1, protocol=443)
    with pytest.raises(ValueError):
        s.register_event('100', 'Device is reachable', 1, protocol='https')