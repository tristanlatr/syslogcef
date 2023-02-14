import logging
import socket
import uuid
from typing import Any, Dict, TYPE_CHECKING, Type

if TYPE_CHECKING:
    from typing import Protocol
else:
    Protocol = object

from rfc5424logging import Rfc5424SysLogHandler
from cefevent import CEFEvent
from cefevent.syslog import Syslog

class SyslogSenderFactory(Protocol):
    def __call__(self, host:str, port:int=514, protocol:str="UDP") -> 'SyslogSender':
        ...

class SyslogSender(Protocol):
    def send(self, msg:str) -> None:...

class CEFSender:
    """
    Base class to send CEF messages.
    """

    class EventMeta:
        """
        Wrap a CEF event definition.
        """

        def __init__(self, signatureId:str, 
                    name:str, 
                    severity:int, 
                    **fields:Any) -> None:

            self.fields = dict(
                signatureId = signatureId,
                name = name,
                severity = severity,
            )
            if fields:
                self.fields.update(fields)

    def __init__(self, syslog_sender:SyslogSender, **fields:Any ) -> None:
        """
        Create a CEFSender instance. 
        
        You might want to use SyslogCEFSender to create a sender from syslog server hostname directly.
        """
        
        self.syslog_sender = syslog_sender

        self.fields = {}
        if fields:
            self.fields.update(fields)

        self.registered_events:Dict[str, CEFSender.EventMeta] = {}

    def register_event(self, signatureId:str, name:str, severity:int, **fields:Any) -> None:
        """
        Register a new event definition.
        """
        self.registered_events[signatureId] = CEFSender.EventMeta(
            signatureId=signatureId, 
            name=name, 
            severity=severity,
            **fields
        )
        
        # try to build a CEF message to raise ValueError if the Event definition is invalid
        self._build_cef(signatureId)

    def _build_cef(self, signatureId:str, **fields:Any) -> str:
        event_meta = self.registered_events[signatureId]

        _fields: Dict[str, Any] = {}
        _fields.update(self.fields)
        _fields.update(event_meta.fields)
        _fields.update(fields)

        cef = CEFEvent(strict=True)

        for k,v in _fields.items():
            try:
                cef.set_field(k,v)
            except ValueError:
                if isinstance(v, str):
                    cef.set_field(k,v[:1022])
                else:
                    raise

        msg = cef.build_cef()
        assert isinstance(msg, str)
        return msg

    def send(self, signatureId:str, **fields:Any) -> None:
        """
        Send a CEF message. 

        Args:
            signatureId: ID of the registered event.
            **fields: Additional fields to include into the CEF message, like ::
                message="Error #28", sourceHostName="127.0.0.1"
        
        Raises:
            ValueError: If the a field has invalid value.
        """
        self.syslog_sender.send(self._build_cef(signatureId, **fields))

class Rfc3164SyslogSender(SyslogSender):
    """
    `rfc3164 <https://datatracker.ietf.org/doc/html/rfc3164>`_ sender.
    """
    def __init__(self, host: str, port: int = 514, protocol: str = "UDP"):
        assert protocol in ["TCP", "UDP"], f"Invalid protocol {protocol!r}, please choose 'TCP' or 'UDP'."
        self.host = host
        self.port = port
        self.protocol = protocol
        
        self.syslog = Syslog(host=host, port=port, protocol=protocol)
    
    def send(self, msg: str) -> None:
        self.syslog.notice(msg)

cefeventSyslogSender = Rfc3164SyslogSender # for compatibility, do not use in new code

class Rfc5424SyslogSender(SyslogSender):
    """
    `rfc5424 <https://datatracker.ietf.org/doc/html/rfc5424>`_ sender.
    """
    def __init__(self, host: str, port: int = 514, protocol: str = "UDP"):
        assert protocol in ["TCP", "UDP"], f"Invalid protocol {protocol!r}, please choose 'TCP' or 'UDP'."

        logger_name = f'syslogcef-{uuid.uuid4()}'
        self.logger = logging.getLogger(logger_name)
        
        sh: Rfc5424SysLogHandler = Rfc5424SysLogHandler(
            address=(host, port),
            socktype=socket.SOCK_STREAM if protocol=='TCP' else socket.SOCK_DGRAM,  # Use TCP or UDP
            appname='syslogcef',
            enterprise_id=42, 
            msg_as_utf8=True, 
            utc_timestamp=True
        )
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(sh)
    
    def send(self, msg: str) -> None:
        self.logger.info(msg)

class StdoutSyslogSender(SyslogSender):
    """
    Send CEF messages to stdout.
    """
    def send(self, msg:str) -> None:
        print(msg)

class CompositeSyslogSender(SyslogSender):
    """
    Send CEF messages to several underlying senders.
    """
    def __init__(self, *senders:SyslogSender) -> None:
        self.senders = senders
    def send(self, msg:str) -> None:
        for sender in self.senders:
            sender.send(msg)

class SyslogCEFSender(CEFSender):
    """
    Main object to easily send CEF messages to a syslog server.

    You might want to use CEFSender to have more flexibility.
    """

    def __init__(self, host: str, 
                port: int,
                protocol:str,
                syslog_sender_class:SyslogSenderFactory=Rfc5424SyslogSender,
                **fields: Any) -> None:
        """
        Create a SyslogCEFSender.
        """
        super().__init__(syslog_sender_class(host=host, port=port, protocol=protocol), **fields)
