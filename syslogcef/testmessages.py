"""
Sends a few testing messages to the configured syslog server.
"""
import argparse
import socket

def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sends 3 testing messages to the configured syslog server.")
    parser.add_argument('--host', metavar="HOST",help="Syslog server host.", required=True)
    parser.add_argument('--port', metavar="PORT", help="Syslog server port.", required=True)
    parser.add_argument('--protocol', metavar="'TCP' or 'UDP'", help="Syslog server protocol.", required=True)
    return parser

if __name__ == "__main__":
    from syslogcef import SyslogCEFSender, __version__

    args = get_parser().parse_args()

    syslog = SyslogCEFSender(
        host=args.host, 
        port=args.port, 
        protocol=args.protocol, 
        deviceProduct='syslogcef.testmessages', 
        deviceVendor='syslogcef',
        deviceVersion=__version__.__version__, 
        sourceHostName=socket.gethostname(), )

    syslog.register_event('1113-100', name='Testing syslogcef OK', severity=0)
    syslog.register_event('1113-101', name='Testing syslogcef WARN', severity=5)
    syslog.register_event('1113-102', name='Testing syslogcef ERROR', severity=9, 
        reason="This is only a test.")

    syslog.send('1113-100', message="The syslogcef module is working properly.")
    syslog.send('1113-101', message="The syslogcef module is still working properly.")
    syslog.send('1113-102', message="The syslogcef module is working properly again.")