#!/usr/bin/env python

import pexpect
import sys

# Start the subprocess
child = pexpect.spawn("./ascp -QT -l300M -L- /Users/etuk/Dropbox/tgac/data/888_LIB6842_LDI5660_ACTTGA_L002_R2_013.fastq Webin-39962@webin.ebi.ac.uk:.",timeout=None)
# redirect output to stdout
# child.logfile_read = sys.stdout

# Assumes the prompt is "password:"
child.expect("Password:")
child.sendline("toni12")

# Wait for the process to close its output
child.expect(pexpect.EOF)