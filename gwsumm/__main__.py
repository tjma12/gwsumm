#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Gravitational-wave interferometer summary information system.

This module provides the command-line interface to the GWSumm package,
allowing generation of detector summary information
"""

from .version import version as __version__
__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'

import os
import datetime
import optparse
import re
import calendar

from dateutil.relativedelta import relativedelta

from lal import gpstime

from gwpy.detector import Channel
from gwpy.segments import Segment
from gwpy.time import Time

from . import globalv
from .config import *
from .tabs import *
from .utils import *
from .state import *

# set matplotlib backend
from matplotlib import use
use('Agg')

# find channels
re_channel = re.compile('[A-Z]\d:[A-Z]+-[A-Z0-9_]+\Z')

# XXX HACK: disable colon separator in ConfigParser
GWSummConfigParser.OPTCRE = re.compile(
    r'(?P<option>[^=\s][^=]*)\s*(?P<vi>[=])\s*(?P<value>.*)$')

VERBOSE = False
PROFILE = False

# set mode enum
SUMMARY_MODE_DAY = 0
SUMMARY_MODE_MONTH = 1
SUMMARY_MODE_YEAR = 2
SUMMARY_MODE_WEEK = 3
SUMMARY_MODE_GPS = 4
MODE_NAME = {SUMMARY_MODE_GPS: 'GPS',
             SUMMARY_MODE_DAY: 'DAY',
             SUMMARY_MODE_WEEK: 'WEEK',
             SUMMARY_MODE_MONTH: 'MONTH',
             SUMMARY_MODE_YEAR: 'YEAR'}

# ----------------------------------------------------------------------------
# Command-line options

usage = 'python -m gwsumm --config-file CONFIG --day YYYYMMDD'

parser = optparse.OptionParser(usage=usage, description=__doc__,
                               formatter=optparse.IndentedHelpFormatter(4))

parser.add_option("-p", "--profile", action="store_true", default=False,
                  help="show second timer with verbose statements, "
                       "default: %default")
parser.add_option("-v", "--verbose", action="store_true", default=False,
                  help="show verbose output, default: %default")
parser.add_option("-V", "--version", action="version",
                  help="show program's version number and exit")
parser.version = __version__

bopts = parser.add_option_group("Basic options")
bopts.add_option('-i', '--ifo', action='store', type='string',
                 metavar='IFO', help="Instrument to process. If this option "
                                     "is set in the [DEFAULT] of any of the "
                                     "INI files, giving it here is redundant.")

copts = parser.add_option_group("Configuration options",
                                "Provide a number of INI-format "
                                "configuration files")
copts.add_option('-f', '--config-file', action='append', type='string',
                 metavar='FILE', default=[],
                 help="INI file for analysis, may be given multiple times")

outopts = parser.add_option_group("Output options")
outopts.add_option('-o', '--output-dir', action='store', type='string',
                   metavar='DIR', default=os.curdir,
                   help="Output directory for summary information, "
                        "default: '%default'")

topts = parser.add_option_group("Time mode options",
                                "Choose a stadard time mode, or a GPS "
                                "[start, stop) interval")
topts.add_option("--day", action="store", type="string", metavar='YYYYMMDD',
                 help="day to process.")
topts.add_option("--week", action="store", type="string", metavar="YYYYMMDD",
                 help="week to process (by starting day).")
topts.add_option("--month", action="store", type="string", metavar="YYYYMM",
                 help="month to process.")
topts.add_option("--year", action="store", type="string", metavar="YYYY",
                 help="year to process.")
topts.add_option("-s", "--gps-start-time", action="store", type="int",
                 metavar="GPSSTART", help="GPS start time")
topts.add_option("-e", "--gps-end-time", action="store", type="int",
                 metavar="GPSEND", help="GPS end time")

opts, args = parser.parse_args()

# read configuration file
config = GWSummConfigParser()
config.optionxform = str
if opts.ifo:
    config.set(None, 'ifo', opts.ifo)
config.read(opts.config_file)
config.files = map(os.path.abspath, opts.config_file)

# parse IFO
try:
    ifo = config.get(DEFAULTSECT, 'ifo')
except NoOptionError:
    raise ValueError("The relevant IFO must be given either from the --ifo "
                     "command-line option, or the [DEFAULT] section of any "
                     "INI file")

# interpolate section names
for section in config.sections():
    if section.startswith('%(ifo)s'):
        s2 = section.replace('%(ifo)s', ifo)
        config._sections[s2] = config._sections.pop(section)

# check time options
N = sum([opts.day is not None, opts.month is not None,
         opts.gps_start_time is not None, opts.gps_end_time is not None])
if N > 1 and not (opts.gps_start_time and opts.gps_end_time):
    raise optparse.OptionValueError("Please give only one of --day, "
                                    "--month, or --gps-start-time and "
                                    "--gps-end-time.")

if opts.day:
    try:
        opts.day = datetime.datetime.strptime(opts.day, "%Y%m%d")
    except ValueError:
        raise optparse.OptionValueError("--day malformed. Please format "
                                        "as YYYYMMDD")
    else:
        opts.gps_start_time = gpstime.utc_to_gps(opts.day)
        opts.gps_end_time = gpstime.utc_to_gps(opts.day +
                                               datetime.timedelta(days=1))
elif opts.week:
    week = opts.week
    try:
        opts.week = datetime.datetime.strptime(opts.week, "%Y%m%d")
    except ValueError:
        raise optparse.OptionValueError("--week malformed. Please format"
                                        " as YYYYMMDD")
    else:
        if config.has_option("calendar", "start-of-week"):
            weekday = getattr(calendar,
                              config.get("calendar", "start-of-week").upper())
            if weekday != opts.week.timetuple().tm_wday:
                msg = ("Cannot process week starting on %s. The "
                       "'start-of-week' option in the [calendar] section "
                       "of the INI file specifies weeks start on %ss."
                       % (week, config.get("calendar", "start-of-week")))
                raise optparse.OptionValueError(msg)
        opts.gps_start_time = gpstime.utc_to_gps(opts.week)
        opts.gps_end_time = gpstime.utc_to_gps(opts.week +
                                               datetime.timedelta(days=7))
# parse month definition
elif opts.month:
    try:
        opts.month = datetime.datetime.strptime(opts.month, "%Y%m")
    except ValueError:
        raise optparse.OptionValueError("--month malformed. Please format"
                                        " as YYYYMM")
    else:
        opts.gps_start_time = gpstime.utc_to_gps(opts.month)
        opts.gps_end_time = gpstime.utc_to_gps(opts.month +
                                               relativedelta(months=1))
elif opts.year:
    try:
        opts.year = datetime.datetime.strptime(opts.year, "%Y")
    except ValueError:
        raise optparse.OptionValueError("--year malformed. Please format"
                                        " as YYYY")
    else:
        opts.gps_start_time = gpstime.utc_to_gps(opts.year)
        opts.gps_end_time = gpstime.utc_to_gps(opts.year +
                                               relativedelta(years=1))
# parse GPS start and stop times
elif opts.gps_start_time or opts.gps_end_time:
    if not (opts.gps_start_time and opts.gps_end_time):
        raise optparse.OptionValueError("Please give both --gps-start-time "
                                        "and --gps-end-time.")
else:
    opts.day = datetime.date(*datetime.datetime.utcnow().timetuple()[:3])
    opts.gps_start_time = int(gpstime.utc_to_gps(opts.day))
    opts.gps_end_time = int(gpstime.utc_to_gps(opts.day +
                                               datetime.timedelta(days=1)))

starttime = Time(float(opts.gps_start_time), format='gps')
endtime = Time(float(opts.gps_end_time), format='gps')
span = Segment(starttime.gps, endtime.gps)
try:
    config.set('general', 'gps-start-time', str(int(starttime.gps)))
except config.NoSectionError:
    config.add_section('general')
    config.set('general', 'gps-start-time', str(int(starttime.gps)))
finally:
    config.set('general', 'gps-end-time', str(int(endtime.gps)))

# set verbose output options
globalv.VERBOSE = opts.verbose
globalv.PROFILE = opts.profile

# set mode
if opts.day:
    mode = SUMMARY_MODE_DAY
elif opts.week:
    mode = SUMMARY_MODE_WEEK
elif opts.month:
    mode = SUMMARY_MODE_MONTH
elif opts.year:
    mode = SUMMARY_MODE_YEAR
else:
    mode = SUMMARY_MODE_GPS

globalv.MODE = mode

# -----------------------------------------------------------------------------
# Setup

vprint("""
------------------------------------------------------------------------------
Welcome to the GW summary information system command-line interface
------------------------------------------------------------------------------

You have selected %s mode.
Start time %s (%s)
End time: %s (%s)
""" % (MODE_NAME[mode], starttime.utc.iso, starttime.gps,
       endtime.utc.iso, endtime.gps))

# parse channel grouns into individual sections
for section in config.sections():
    if re.match('channels[-\s]', section):
        items = dict(config.nditems(section))
        try:
            names = items.pop('channels').split(',')
        except KeyError:
            raise NoOptionError('channels', section)
        for name in names:
            config.add_section(name)
            for key, val in items.iteritems():
                config.set(name, key, val)

# read custom channel definitions
for section in config.sections():
    if re_channel.match(section):
        if section not in globalv.CHANNELS:
            try:
                globalv.CHANNELS[section] = Channel.query(section)
            except ValueError:
                globalv.CHANNELS[section] = Channel(section)
        for key, val in sorted(config.nditems(section), key=lambda x: x[0]):
            key = re_cchar.sub('_', key.rstrip())
            if key.isdigit():
                if not hasattr(globalv.CHANNELS[section], 'bitmask'):
                    globalv.CHANNELS[section].bitmask = []
                globalv.CHANNELS[section].bitmask.append(val)
            else:
                setattr(globalv.CHANNELS[section], key, eval(val.rstrip()))

# read states
load_states(config)

# build directories
outdir = opts.output_dir
mkdir(outdir)
os.chdir(outdir)
plotdir = 'plots'
mkdir(plotdir)

# -----------------------------------------------------------------------------
# Read HTML configuration

css = [cval for (key, cval) in config.items('html') if re.match('css\d+', key)]
javascript = [jval for (key, jval) in config.items('html') if
              re.match('javascript\d+', key)]


# -----------------------------------------------------------------------------
# Read tabs

# read all tabs
alltabs = []
for section in filter(lambda n: n.startswith('tab-'), config.sections()):
    tab = SummaryTab.from_ini(config, section, plotdir=plotdir)
    alltabs.append(tab)

# sort tabs into hierarchical list
tabs = {}
for tab in alltabs:
    if not tab.parent:
        tabs[tab.name] = tab
for tab in alltabs:
    if tab.parent:
        tab.parent = tabs[tab.parent]
        tab.parent.add_child(tab)

# -----------------------------------------------------------------------------
# Process all tabs

tabs = tabs.values()
tabs.sort(key=lambda t: t.name == 'Summary' and '_' or t.name.lower())

for tab in alltabs:
    tab.process(config=config)

# -----------------------------------------------------------------------------
# Write HTML

# write config page
about = AboutTab('About', parent=None, states=[globalv.STATES[ALLSTATE]])
mkdir(about.path)
about.build_html(css=css, js=javascript, tabs=tabs, config=config.files)

for tab in alltabs:
    mkdir(tab.href)
    page = tab.build_html(css=css, js=javascript, tabs=tabs, about=about.index)

vprint("""
------------------------------------------------------------------------------
All done. Thank you.
------------------------------------------------------------------------------
""")