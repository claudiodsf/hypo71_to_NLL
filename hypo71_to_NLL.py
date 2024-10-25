#!/usr/bin/env python
"""
hypo71_to_NLL.py

This script converts a hypo71 phase file to a NLLoc phase file.

Part of the code is based on SourceSpec (sourcespec.seismicsource.org)

Usage:
    hypo71_to_NLL.py [options] pick_file [output_file]

Arguments:
    pick_file: hypo71 phase file
    output_file: output NLLoc phase file. If not specified, output is written
        to stdout

(c) 2024, Claudio Satriano <satriano@ipgp.fr>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys
import argparse
from datetime import datetime, timedelta


class Pick:
    """
    A pick object
    """
    def __init__(self):
        self.station = ''
        self.flag = ''
        self.phase = ''
        self.polarity = ''
        self.quality = 0
        self.error = 0
        self.time = None

    def to_nlloc(self):
        """
        Convert pick to NLLoc format
        """
        timestr = self.time.strftime('%Y%m%d %H%M %S.%f')
        return (
            f'{self.station:6} ? ? ? {self.phase} {timestr} '
            f'GAU {self.error} 1.0 1.0 1.0'
        )


def _is_hypo71_picks(pick_file):
    with open(pick_file, encoding='ascii') as fp:
        for line in fp:
            # remove newline
            line = line.replace('\n', '')
            # skip separator and empty lines
            stripped_line = line.strip()
            if stripped_line in ['10', '']:
                continue
            # Check if it is a pick line
            # 6th character should be P or empty
            # other character should be digits (date/time)
            if not (line[5] in ['P', ' '] and
                    line[9].isdigit() and
                    line[20].isdigit()):
                raise TypeError(f'{pick_file}: Not a hypo71 phase file')


def _parse_hypo71_pick_line(line, errors):
    """
    Parse a hypo71 pick line

    :param line: hypo71 pick line
    :param errors: list of 5 picking errors

    :return: list of Pick objects or None
    """
    picks = []
    # remove newline
    line = line.replace('\n', '')
    # skip separator and empty lines
    stripped_line = line.strip()
    if stripped_line in ['10', '']:
        return
    # Check if it is a pick line
    # 6th character should be P or empty
    # other character should be digits (date/time)
    if not (line[5] in ['P', ' '] and
            line[9].isdigit() and
            line[20].isdigit()):
        return
    pick = Pick()
    pick.station = line[:4].strip()
    pick.flag = line[4:5]
    pick.phase = line[5:6]
    pick.polarity = line[6:7]
    try:
        pick.quality = int(line[7:8])
    except ValueError:
        # If we cannot read pick quality,
        # we give the pick the lowest quality
        pick.quality = 4
    pick.error = errors[pick.quality]
    timestr = line[9:24].replace(' ', '0')
    # split time str in date and time
    datestr = timestr[:6]
    hour = int(timestr[6:8])
    minute = int(timestr[8:10])
    seconds = float(timestr[10:15])
    milliseconds = int(seconds * 1000)
    pick.time = datetime.strptime(datestr, '%y%m%d')
    pick.time = pick.time + timedelta(
        hours=hour, minutes=minute, milliseconds=milliseconds)
    # Do not store empty picks, which are only used
    # to give a time base for the corresponding S pick
    if pick.phase == 'P':
        picks.append(pick)
    try:
        stime = line[31:36]
    except ValueError:
        return picks
    if stime.strip() == '':
        return picks
    pick2 = Pick()
    pick2.station = pick.station
    pick2.flag = line[36:37]
    pick2.phase = line[37:38]
    pick2.polarity = line[38:39]
    try:
        pick2.quality = int(line[39:40])
    except ValueError:
        # If we cannot read pick quality,
        # we give the pick the lowest quality
        pick2.quality = 4
    pick2.error = errors[pick2.quality]
    # pick2.time has the same date, hour and minutes
    # than pick.time
    # We therefore make a copy of pick.time,
    # and set seconds and microseconds to 0
    pick2.time = pick.time.replace(second=0, microsecond=0)
    # finally we add stime
    stime = timedelta(seconds=float(stime))
    pick2.time += stime
    picks.append(pick2)
    return picks


def parse_hypo71_picks(pick_file, errors):
    """
    Parse hypo71 picks file

    :param pick_file: hypo71 picks file
    :param errors: list of 5 picking errors

    :return: list of lists of Pick objects
    """
    try:
        _is_hypo71_picks(pick_file)
    except TypeError as err:
        sys.exit(err)
    all_picks = []
    picks = []
    with open(pick_file, encoding='ascii') as fp:
        for line in fp:
            if line.strip() in ['10']:
                all_picks.append(picks)
                picks = []
            _picks = _parse_hypo71_pick_line(line, errors)
            if _picks:
                picks.extend(_picks)
    return all_picks


def parse_args():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description='Convert hypo71 phase file to NLLoc phase file')
    parser.add_argument('pick_file', help='hypo71 phase file')
    parser.add_argument(
        'output_file', default=None, nargs='?',
        help='output NLLoc phase file. If not specified, output is written to '
        'stdout'
    )
    parser.add_argument(
        '--errors', '-e', type=str, default='0.01,0.02,0.03,0.04,0.05',
        help='Comma-separated list of 5 picking errors (in seconds) to be '
        'associated to hypo71 pick qualities (default: %(default)s)'
    )
    # check if errors are valid
    args = parser.parse_args()
    try:
        args.errors = args.errors.split(',')
        errors = [float(args.errors[i]) for i in range(5)]
        args.errors = errors
    except IndexError:
        parser.error('You must specify 5 values for --errors')
    except ValueError:
        parser.error('Invalid values for --errors')
    return args


def run():
    """
    Run the script
    """
    args = parse_args()
    all_picks = parse_hypo71_picks(args.pick_file, args.errors)
    if args.output_file:
        fp = open(args.output_file, 'w', encoding='utf-8')
    else:
        fp = sys.stdout
    for picks in all_picks:
        for pick in picks:
            fp.write(pick.to_nlloc() + '\n')
        fp.write('\n\n')
    if args.output_file:
        fp.close()
        print(f'Output written to {args.output_file}')


def main():
    """Main function. Catch KeyboardInterrupt."""
    try:
        # Avoid broken pipe errors, e.g., when piping output to head
        # pylint: disable=import-outside-toplevel
        from signal import signal, SIGPIPE, SIG_DFL
        signal(SIGPIPE, SIG_DFL)
    except ImportError:  # If SIGPIPE is not available (win32),
        pass
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == '__main__':
    main()
