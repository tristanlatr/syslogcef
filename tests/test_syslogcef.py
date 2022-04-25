import uuid
import typing as t
import logging
import sys

from syslogcef import _CEFSender

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

def setup_stdout_logger(
    name: str,
    verbose: bool = False,
    quiet: bool = False,
    ) -> logging.Logger:
    """
    Utility to setup a stdout logger.
    """
    format_string = "%(message)s"
    if verbose: verb_level = logging.DEBUG
    elif quiet: verb_level = logging.ERROR
    else: verb_level = logging.INFO
    log = logging.getLogger(name)
    log.setLevel(verb_level)
    std = logging.StreamHandler(sys.stdout)
    std.setLevel(verb_level)
    std.setFormatter(logging.Formatter(format_string))
    log.addHandler(std)
    return log


def new_logger() -> 'str':
    logger_name = f'test-syslogcef-{uuid.uuid4()}'
    setup_stdout_logger(logger_name)
    return logger_name

def test_syslogcef(capsys:CapSys) -> None:

    s = _CEFSender(new_logger(), deviceProduct='test-syslogcef', deviceVendor='Github',
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