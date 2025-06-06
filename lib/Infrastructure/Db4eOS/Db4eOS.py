"""
lib/Infrastructure/Db4eOS/Db4eOS.py
"""

import psutil

# Process names
class Db4eOS():

    def get_pid(self, proc_name):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc_name in proc.info['name']:
                return proc.info['pid']
        return None        

