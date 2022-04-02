import json
import logging
import datetime
import argparse

from dl24 import DL24


def set_current(dl24: DL24, value: float):
    print("set_current", value)
    dl24.set_current(value)


def set_voltage_cutoff(dl24: DL24, value: float):
    print("set_voltage_cutoff", value)
    dl24.set_voltage_cutoff(value)


def set_timer(dl24: DL24, value: float):
    td = datetime.timedelta(seconds=value)
    print("set_timer", td)
    dl24.set_timer(td)


def enable(dl24: DL24):
    print("enable")
    dl24.enable()


def disable(dl24: DL24):
    print("disable")
    dl24.disable()


def reset_counters(dl24: DL24):
    print("reset_counters")
    dl24.reset_counters()


def timedelta_to_str(x: datetime.timedelta):
    seconds = int(x.total_seconds())
    hours = seconds // 3600
    minutes = (seconds // 60) % 60
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def read(dl24: DL24, out_format: str):
    is_on = dl24.get_is_on()
    voltage = dl24.get_voltage()
    current = dl24.get_current()
    energy = dl24.get_energy()
    charge = dl24.get_charge()
    time = dl24.get_time()
    temp = dl24.get_temp()
    current_limit = dl24.get_current_limit()
    voltage_cutoff = dl24.get_voltage_cutoff()
    timer = dl24.get_timer()

    if out_format == "text":
        print("enabled", is_on)
        print("voltage", voltage)
        print("current", current)
        print("energy", energy)
        print("charge", charge)
        print("time", time)
        print("temperature", temp)
        print("current_limit", current_limit)
        print("voltage_cutoff", voltage_cutoff)
        print("timer", timer)
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


def main():
    logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    argparser = argparse.ArgumentParser()
    argparser.set_defaults(cmd=lambda: None, cmd_args=lambda x: [])
    argparser.add_argument('-p', '--path', type=str, metavar="PATH", required=True)

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

    dl24 = DL24(args.path)

    args.cmd(dl24, *args.cmd_args(args))


main()
