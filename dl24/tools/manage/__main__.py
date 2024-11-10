import asyncio
import json
import logging
import datetime
import argparse

from dl24 import DL24
from transports.TransportSerial import TransportSerial


async def set_current(dl24: DL24, value: float):
    print("set_current", value)
    await dl24.set_current(value)


async def set_voltage_cutoff(dl24: DL24, value: float):
    print("set_voltage_cutoff", value)
    await dl24.set_voltage_cutoff(value)


async def set_timer(dl24: DL24, value: float):
    td = datetime.timedelta(seconds=value)
    print("set_timer", td)
    await dl24.set_timer(td)


async def enable(dl24: DL24):
    print("enable")
    await dl24.enable()


async def disable(dl24: DL24):
    print("disable")
    await dl24.disable()


async def reset_counters(dl24: DL24):
    print("reset_counters")
    await dl24.reset_counters()


def timedelta_to_str(x: datetime.timedelta):
    seconds = int(x.total_seconds())
    hours = seconds // 3600
    minutes = (seconds // 60) % 60
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


async def read(dl24: DL24, out_format: str):
    is_on = await dl24.get_is_on()
    voltage = await dl24.get_voltage()
    current = await dl24.get_current()
    energy = await dl24.get_energy()
    charge = await dl24.get_charge()
    time = await dl24.get_time()
    temp = await dl24.get_temp()
    current_limit = await dl24.get_current_limit()
    voltage_cutoff = await dl24.get_voltage_cutoff()
    timer = await dl24.get_timer()

    if out_format == "text":
        def format_value(name, value, unit):
            value_str = f"{value}"
            value_str += f" {unit or '': <3s}"
            return f"{name: >20s}: {value_str: >12s}"

        print(format_value("enabled", "yes" if is_on else "no", None))
        print(format_value("voltage", voltage, "V"))
        print(format_value("current", current, "A"))
        print(format_value("energy", energy, "Wh"))
        print(format_value("charge", charge, "Ah"))
        print(format_value("time", time, None))
        print(format_value("temperature", temp, "°C"))
        print(format_value("current_limit", current_limit, "A"))
        print(format_value("voltage_cutoff", voltage_cutoff, "V"))
        print(format_value("timer", timer, None))
    elif out_format == "json":
        print(json.dumps({
            "enabled": is_on,
            "voltage": voltage,
            "current": current,
            "energy": energy,
            "charge": charge,
            "time": timedelta_to_str(time),
            "temperature": temp,
            "current_limit": current_limit,
            "voltage_cutoff": voltage_cutoff,
            "timer": timedelta_to_str(timer),
        }, indent=2))


async def app():
    argparser = argparse.ArgumentParser()
    argparser.set_defaults(cmd=lambda: None, cmd_args=lambda x: [])
    argparser.add_argument('-p', '--path', type=str, metavar="PATH", required=True)
    argparser.add_argument('-d', '--debug', action='store_true')

    subparsers = argparser.add_subparsers(title='subcommands', description='valid subcommands', help='additional help')

    sparser = subparsers.add_parser('set-current')
    sparser.set_defaults(cmd=set_current, cmd_args=lambda x: (x.value,))
    sparser.add_argument("value", type=float)

    sparser = subparsers.add_parser('set-voltage-cutoff')
    sparser.set_defaults(cmd=set_voltage_cutoff, cmd_args=lambda x: (x.value,))
    sparser.add_argument("value", type=float)

    sparser = subparsers.add_parser('set-timer')
    sparser.set_defaults(cmd=set_timer, cmd_args=lambda x: (x.value,))
    sparser.add_argument("value", type=float)

    sparser = subparsers.add_parser('enable')
    sparser.set_defaults(cmd=enable)

    sparser = subparsers.add_parser('disable')
    sparser.set_defaults(cmd=disable)

    sparser = subparsers.add_parser('reset')
    sparser.set_defaults(cmd=reset_counters)

    sparser = subparsers.add_parser('read')
    sparser.set_defaults(cmd=read, cmd_args=lambda x: (x.format,))
    sparser.add_argument("-f", "--format", choices=["text", "json"], default="text")

    args = argparser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format="[%(asctime)s] [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    transport = TransportSerial(args.path)
    dl24 = DL24(transport)

    await args.cmd(dl24, *args.cmd_args(args))


def main():
    asyncio.run(app())


if __name__ == "__main__":
    main()
