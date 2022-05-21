import os
import csv
import sys
import logging
import datetime
import argparse
import time

from dl24 import DL24, DL24Error


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-p', '--path', type=str, metavar="PATH", required=True)
    argparser.add_argument('-o', '--output', type=str, metavar="PATH")
    argparser.add_argument('-a', '--append', action='store_true')
    argparser.add_argument('-d', '--debug', action='store_true')
    argparser.add_argument('--override', action='store_true')

    args = argparser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format="[%(asctime)s] [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    out_path = args.output

    csvfile = None
    wr = None
    if out_path is not None:
        exists = os.path.exists(out_path)

        if exists and not (args.append or args.override):
            print("Output file already exists. Specify --append or --override")
            sys.exit(1)

        if args.append:
            is_new = not exists
            csvfile = open(out_path, 'a', newline='')
        else:
            is_new = True
            csvfile = open(out_path, 'w', newline='')

        wr = csv.writer(csvfile)
        if is_new:
            wr.writerow(['date', 'voltage', 'current', 'power', 'energy', 'charge', 'temp', 'time_seconds', 'time_str'])

    dl24 = DL24(args.path)

    while True:
        try:
            dl24.wait_for_broadcast()
            voltage = dl24.get_voltage()
            current = dl24.get_current()
            temp = dl24.get_temp()
            energy = dl24.get_energy()
            charge = dl24.get_charge()
            on_time = dl24.get_time()

            days = on_time.days
            seconds = on_time.seconds
            hours = seconds // 3600
            minutes = (seconds // 60) % 60
            seconds = seconds % 60

            time_sec = int(on_time.total_seconds())
            time_str = f"{days:01d}d {hours:02d}:{minutes:02d}:{seconds:02d}"
            data = [
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                f"{voltage:.2f}",
                f"{current:.2f}",
                f"{voltage * current:.2f}",
                f"{energy:.2f}",
                f"{charge:.2f}",
                f"{temp:.0f}",
                f"{time_sec}",
                time_str,
            ]

            s = f"\r\u001b[2K{voltage:5.02f} V | {current:5.2f} A | {voltage * current:5.2f} W | {energy:6.2f} Wh | {charge:5.2f} Ah | {time_str} | {temp} °C"
            print(s, end='')

            if csvfile is not None and wr is not None:
                wr.writerow(data)
                csvfile.flush()

            time.sleep(1)
        except DL24Error:
            pass


if __name__ == "__main__":
    main()
