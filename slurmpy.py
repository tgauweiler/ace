r"""
The MIT License (MIT)

Copyright (c) 2015 Brent Pedersen - Bioinformatics

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

https://github.com/brentp/slurmpy

# send in job name and kwargs for slurm params:
>>> s = Slurm("job-name", {"account": "ucgd-kp", "partition": "ucgd-kp"})
>>> print(str(s))
#!/bin/bash
<BLANKLINE>
#SBATCH -e logs/job-name.%J.err
#SBATCH -o logs/job-name.%J.out
#SBATCH -J job-name
<BLANKLINE>
#SBATCH --account=ucgd-kp
#SBATCH --partition=ucgd-kp
<BLANKLINE>
set -eo pipefail -o nounset
<BLANKLINE>
__script__

>>> job_id = s.run("rm -f aaa; sleep 10; echo 213 > aaa", name_addition="", tries=1)

>>> job = s.run("cat aaa; rm aaa", name_addition="", tries=1, depends_on=[job_id])

"""
from __future__ import print_function

import sys
import os
import subprocess
import tempfile
import atexit
import hashlib
import datetime

TMPL = """\
#!/bin/bash

#SBATCH -e {log_directory}/{name}.%J.err
#SBATCH -o {log_directory}/{name}.%J.out
#SBATCH -J {name}

{header}


__script__"""


def tmp(suffix=".sh"):
    t = tempfile.mktemp(suffix=suffix)
    atexit.register(os.unlink, t)
    return t


class Slurm(object):
    def __init__(self, name, slurm_kwargs=None, tmpl=None, date_in_name=True, scripts_dir="slurm-scripts/", log_directory=None):
        if slurm_kwargs is None:
            slurm_kwargs = {}
        if tmpl is None:
            tmpl = TMPL
        if log_directory is None:
            self.log_directory = 'logs'
        else:
            self.log_directory = log_directory

        header = []
        for k, v in slurm_kwargs.items():
            if len(k) > 1:
                if v is None or len(v) == 0:
                    k = "--" + k
                    header.append("#SBATCH %s" % k)
                else:
                    k = "--" + k + "="
                    header.append("#SBATCH %s%s" % (k, v))
            else:
                k = "-" + k + " "
                header.append("#SBATCH %s%s" % (k, v))
        self.header = "\n".join(header)
        self.name = "".join(x for x in name.replace(
            " ", "-") if x.isalnum() or x == "-")
        self.tmpl = tmpl
        self.slurm_kwargs = slurm_kwargs
        if scripts_dir is not None:
            self.scripts_dir = os.path.abspath(scripts_dir)
        else:
            self.scripts_dir = None
        self.date_in_name = bool(date_in_name)

    def __str__(self):
        return self.tmpl.format(name=self.name, header=self.header, log_directory=self.log_directory)

    def _tmpfile(self):
        if self.scripts_dir is None:
            return tmp()
        else:
            if not os.path.exists(self.scripts_dir):
                os.makedirs(self.scripts_dir)
            return "%s/%s.sh" % (self.scripts_dir, self.name)

    def run(self, command, name_addition=None, cmd_kwargs=None, _cmd="sbatch", tries=1, depends_on=None):
        """
        command: a bash command that you want to run
        name_addition: if not specified, the sha1 of the command to run
                       appended to job name. if it is "date", the yyyy-mm-dd
                       date will be added to the job name.
        cmd_kwargs: dict of extra arguments to fill in command
                   (so command itself can be a template).
        _cmd: submit command (change to "bash" for testing).
        tries: try to run a job either this many times or until the first
               success.
        depends_on: job ids that this depends on before it is run (users 'afterok')
        """
        if name_addition is None:
            name_addition = ""
            # name_addition = hashlib.sha1(command.encode("utf-8")).hexdigest()

        if self.date_in_name:
            name_addition += "-" + str(datetime.date.today())
        name_addition = name_addition.strip(" -")

        if cmd_kwargs is None:
            cmd_kwargs = {}

        n = self.name
        self.name = self.name.strip(" -")
        self.name += "-" + name_addition.strip(" -")
        args = []
        for k, v in cmd_kwargs.items():
            args.append("export %s=%s" % (k, v))
        args = "\n".join(args)

        tmpl = str(self).replace("__script__", args + "\n###\n" + command)
        if depends_on is None:
            depends_on = []

        if not os.path.exists(self.log_directory + '/'):
            os.makedirs(self.log_directory)

        with open(self._tmpfile(), "w") as sh:
            sh.write(tmpl)

        job_id = None
        for itry in range(1, tries + 1):
            args = [_cmd]
            args.extend(["--dependency=afterok:%d" % d for d in depends_on])
            if itry > 1:
                mid = "--dependency=afternotok:%d" % job_id
                args.append(mid)
            args.append(sh.name)
            # print(args)
            res = subprocess.check_output(args).strip()
            # print("submitted:", res, file=sys.stderr)
            self.name = n
            if not res.startswith(b"Submitted batch"):
                return None
            j_id = int(res.split()[-1])
            if itry == 1:
                job_id = j_id
        return job_id


if __name__ == "__main__":
    import doctest

    doctest.testmod()
