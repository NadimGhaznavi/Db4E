"""
Mining/MoneroD/MoneroD.py
"""

import os, sys, time, re

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eConfig.Db4eConfig import Db4eConfig

class MoneroD():
    """
    This class retrieves status information from the Monero daemon.
    """

    def __init__(self):
        # Load the db4e configuration
        config = Db4eConfig()
        self._install_dir = config.config['monerod']['install_dir']
        self._log_dir     = config.config['monerod']['log_dir']
        self._log_file    = config.config['monerod']['log_file']
        self._run_dir     = config.config['monerod']['run_dir']
        self._stdin_pipe  = config.config['monerod']['stdin_pipe']

    def log_file(self):
        return os.path.join(self._install_dir, self._log_dir, self._log_file)

    def get_height(self):
        log_file = self.log_file()
        log_handle = open(log_file, 'r', buffering=1)
        self._loglines = self._log_generator(log_handle)

        self._send_cmd('status')
        try:
            for log_line in self._loglines:
                height = self._found_height(log_line)
                if height != False:
                    print(f"{height}")
                    break

        except KeyboardInterrupt:
            print("Monitoring stopped by user.")

    def stdin_pipe(self):
        return os.path.join(self._install_dir, self._run_dir, self._stdin_pipe)

    def _found_height(self, log_line):
        """
        Check if the log line contains a status message.

        Here is a sample status log line:
        2025-05-29 23:58:20.633	    7faec8b326c0	INFO	msgwriter	src/common/scoped_message_writer.h:102	Height: 199892/3422606 (5.8%) on mainnet, not mining, net hash 21.24 MH/s, v1, 7(out)+3(in) connections, uptime 0d 0h 9m 26s

        Here it is again, broken up by whitespace for clarity:
        
        2025-05-29 23:58:20.633
        7faec8b326c0
        INFO
        msgwriter
        src/common/scoped_message_writer.h:102
        Height: 199892/3422606
        (5.8%) on mainnet, 
        not mining, 
        net hash 21.24 MH/s, 
        v1, 
        7(out)+3(in) connections, 
        uptime 0d 0h 9m 26s
        """
        pattern = r".*(?P<height>Height: \d+/\d+).*" #v1, \d+\(out\)(?P<conn_out>\d+).*" #\(in\) connections).*" # , uptime \d+d \d+h \d+m \d+s).*"
        match = re.search(pattern=pattern, string=log_line)
        if match:
            height = match.group('height')
            return height
        else:
            return False

    def _log_generator(self, log_handle):
        """
        Generator to yield lines from the log file.
        """
        log_handle.seek(0, os.SEEK_END)  # Move to the end of the file
        while True:
            log_line = log_handle.readline()
            if not log_line:
                time.sleep(1)
                continue

            yield log_line.strip()

    def _send_cmd(self, cmd):
        """
        Send a command to the Monero daemon via the stdin pipe.
        """
        stdin_pipe = self.stdin_pipe()
        if not os.path.exists(stdin_pipe):
            print(f"ERROR: Monerod STDIN pipe does not exist: {stdin_pipe}")
            return

        with open(stdin_pipe, 'w') as pipe:
            pipe.write(cmd + '\n')
            pipe.flush()
    
