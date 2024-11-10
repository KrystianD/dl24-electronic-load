from dataclasses import dataclass

from .transports.ITransport import ITransport
from .transports.TransportSerial import TransportSerial
from .transports.TransportTCP import TransportTCP


async def connect_to_transport(path: str) -> ITransport:
    transport: ITransport
    if path.startswith("tcp:"):
        _, host, port = path.split(":")
        tcp_transport = TransportTCP(host, int(port))
        await tcp_transport.connect()
        transport = tcp_transport
    else:
        transport = TransportSerial(path)

    return transport
