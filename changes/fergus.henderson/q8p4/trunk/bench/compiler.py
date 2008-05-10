# benchmark -- automated system for testing distcc correctness
# and performance on various source trees.

# Copyright (C) 2002, 2003 by Martin Pool

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

import buildutil
import os

class CompilerSpec:
    """Describes a compiler/make setup.

    Used to define different situations such as local compilation, and
    various degrees of parallelism."""

    def __init__(self, cc='gcc', cxx='c++', make_opts='',
                 pump_cmd='', num_hosts=1, host_opts='',
                 name=None):
        self.cc = cc
        self.cxx = cxx
        self.make_opts = make_opts
        self.host_opts = host_opts
        self.pump_cmd = pump_cmd
        self.num_hosts = num_hosts
        self.host_opts = host_opts
        self.name = name or (self.pump_cmd + self.cc + "__" +
                             self.make_opts).replace(' ', '_')


def default_compilers():
    return [parse_opt('local,h1,j1'),
            parse_opt('dist,h16,j8'),
            parse_opt('dist,h16,j16'),
            parse_opt('dist,h16,j32'),
            parse_opt('dist,h16,j64'),
            parse_opt('pump,h16,j8'),
            parse_opt('pump,h16,j16'),
            parse_opt('pump,h16,j32'),
            parse_opt('pump,h16,j64'),
            parse_opt('dist,h32,j8'),
            parse_opt('dist,h32,j16'),
            parse_opt('dist,h32,j32'),
            parse_opt('dist,h32,j64'),
            parse_opt('pump,h32,j8'),
            parse_opt('pump,h32,j16'),
            parse_opt('pump,h32,j32'),
            parse_opt('pump,h32,j64'),
            ]

def parse_opt(optarg):
    """Parse command-line specification of a compiler

    XXX: I don't really know what the best syntax for this is.  For
    the moment, it is "local", "dist", or "pump", followed by ",h"
    and the number of hosts to use, followed by ",j" and the number
    of jobs to use (for the -j option to make).
    """
    where, hosts, jobs = optarg.split(',')
    if hosts.startswith("h"):
      hosts = int(hosts[1:])
      max_hosts = buildutil.count_hosts(os.getenv("DISTCC_HOSTS"))
      if hosts > max_hosts:
        print ("Warning: can't use %d hosts: DISTCC_HOSTS only has %d" %
               (hosts, max_hosts))
        hosts = max_hosts
    else:
      raise ValueError, ("invalid compiler option: "
                         "expecting '...,h<NUMBER OF HOSTS>,...', found %s"
                         % `hosts`)
    if jobs.startswith("j"):
      jobs = int(jobs[1:])
    else:
      raise ValueError, ("invalid compiler option: "
                         "expecting '...,j<NUMBER OF JOBS>', found %s"
                         % `hosts`)
    if where == 'local':
        return CompilerSpec(name='local_%02d' % jobs,
                            cc='cc',
                            cxx='c++',
                            num_hosts=1,
                            make_opts='-j%d' % jobs)
    elif where == 'dist':
        return CompilerSpec(name='dist_h%02d_j%02d' % (hosts, jobs),
                            cxx='distcc c++',
                            cc='distcc cc',
                            num_hosts=hosts,
                            make_opts='-j%d' % jobs)
    elif where == 'lzo':
        return CompilerSpec(name='lzo_h%02d_j%02d' % (hosts, jobs),
                            cxx='distcc c++',
                            cc='distcc cc',
                            num_hosts=hosts,
                            host_opts=",lzo",
                            make_opts='-j%d' % jobs)
    elif where == 'pump':
        return CompilerSpec(name='pump_h%02d_j%02d' % (hosts, jobs),
                            cxx='distcc c++',
                            cc='distcc cc',
                            pump_cmd='pump ',
                            num_hosts=hosts,
                            host_opts=",cpp,lzo",
                            make_opts='-j%d' % jobs)
    else:
      raise ValueError, ("invalid compiler option: don't understand %s"
                         % `where`)