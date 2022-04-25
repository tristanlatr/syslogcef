import logging
import socket
import uuid
from typing import Any, Dict, Union

from rfc5424logging import Rfc5424SysLogHandler
from cefevent import CEFEvent

class _CEFSender:
    """
    Base class to send CEF messages to logger.
    """

    class _EventMeta:
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

    def __init__(self, logger:Union[str, logging.Logger], **fields:Any ) -> None:
        """
        Create a _CEFSender instance. 
        
        You might want to use SyslogCEFSender() to create a sender from syslog server hostname directly.
        """
        
        self.logger = logging.getLogger(logger) if isinstance(logger, str) else logger

        self.fields = {}
        if fields:
            self.fields.update(fields)

        self.registered_events:Dict[str, _CEFSender._EventMeta] = {}

    def register_event(self, signatureId:str, name:str, severity:int, **fields:Any) -> None:
        """
        Register a new event definition.
        """
        self.registered_events[signatureId] = _CEFSender._EventMeta(
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
        self.logger.info(self._build_cef(signatureId, **fields))

class SyslogCEFSender(_CEFSender):
    """
    Main object to easily send CEF messages to a syslog server.
    """

    def __init__(self, host: str, 
                port: str,
                protocol:str,
                **fields: Any) -> None:
        """
        Create a SyslogCEFSender.
        """
        
        assert protocol in ["TCP", "UDP"], f"Invalid protocol {protocol!r}, please choose 'TCP' or 'UDP'."
        
        logger_name = f'syslogcef-{uuid.uuid4()}'
        logger = logging.getLogger(logger_name)
        
        sh: Rfc5424SysLogHandler = Rfc5424SysLogHandler(
            address=(host, port),
            socktype=socket.SOCK_STREAM if protocol=='TCP' else socket.SOCK_DGRAM,  # Use TCP or UDP
            appname='syslogcef',
            enterprise_id=42, 
            msg_as_utf8=True, 
            utc_timestamp=True
        )
        logger.setLevel(logging.DEBUG)
        logger.addHandler(sh)

        super().__init__(logger, **fields)