"""
Mining/MiningReports/MiningReports.py
"""

import yaml
import os, sys
from datetime import datetime
import shutil
from bson.decimal128 import Decimal128
from decimal import Decimal

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
from MiningDb.MiningDb import MiningDb
from Db4eGit.Db4eGit import Db4eGit
from Db4eLogger.Db4eLogger import Db4eLogger

class MiningReports():
  
    def __init__(self, report_type=None):
        # The db4e logger
        self.log = Db4eLogger('MiningReports')
        # Load the configuration 
        config = Db4eConfig()
        self._db4e_dir      = config.config['db4e']['install_dir']
        self._conf_dir      = config.config['db4e']['conf_dir']
        self._js_dir        = config.config['db4e']['js_dir']
        self._templates_dir = config.config['db4e']['template_dir']
        self._reports_dir   = config.config['db4e']['reports_dir']
        self._md_dir        = config.config['db4e']['md_dir']
        self._web_dir       = config.config['web']['install_dir']
        self._csv_dir       = config.config['web']['csv_dir']

        if report_type:
            self._yaml_file = report_type
        else:
            self._yaml_file = config.config['db4e']['reports']
        
        # Load the report definitions from the YAML file
        self._load_reports()
        # Keep track of the data we've extracted
        self._fresh = {}
        # Get a db4e Git object
        self.git = Db4eGit(self._web_dir)
        # We'll create a reports summary page with these links
        self._report_links = []
        # We need a list of miners for the 'by miner' reports
        self._workers = []

    def run(self):
        """
        Run the mining reports based on the loaded configuration.
        This method should be implemented to generate the reports.
        """
        # This loads the conf/reports/<reports_name>.yml 
        self._load_reports()
        self.log.info(f'Running report ({self._report_file})')
        db4e_dir     = self._db4e_dir
        web_dir      = self._web_dir
        md_dir       = self._md_dir
        reports_dir  = self._reports_dir
        csv_dir      = self._csv_dir
        js_dir       = self._js_dir
        reports_name = self._yaml_file
        
        # CSV file base directory
        if not os.path.exists(os.path.join(web_dir, csv_dir)):
            os.mkdir(os.path.join(web_dir, csv_dir))
        # Reports base directory
        if not os.path.exists(os.path.join(web_dir, reports_dir)):
            os.mkdir(os.path.join(web_dir, reports_dir))
        # Javascript base directory
        if not os.path.exists(os.path.join(web_dir, js_dir)):
            os.mkdir(os.path.join(web_dir, js_dir))

        # Create a fresh reports specific directory e.g.csv/<reports_name>, 
        # pages/reports/<reports_name>, assets/js/<reports_name>
        fq_csv_dir = os.path.join(web_dir, csv_dir, reports_name)
        fq_js_dir = os.path.join(web_dir, js_dir, reports_name)
        fq_reports_dir = os.path.join(web_dir, reports_dir, reports_name)
        for aDir in [ fq_csv_dir, fq_js_dir, fq_reports_dir ]:
            if os.path.exists(aDir):
                # Clean out any old report
                shutil.rmtree(aDir)
            os.mkdir(aDir)

        report_type = None
        for report in self._reports:
            report_type = report['report_type']
            self.run_report(report)

        # Generate a list of reports on a Github MD page
        self._gen_toc(report_type)

        self.git.commit("New db4e reports")
        self.git.push()        

    def run_report(self, report):
        reports_name = self._yaml_file
        reports_dir  = self._reports_dir
        report_type  = report['report_type']
        length       = report['length']
        columns      = report.get('columns', None)

        # The blocksfound reports do not have a sub_type
        Report_type = report_type.capitalize()
        if 'sub_type' in report:
            sub_type = report['sub_type']
            Sub_type = sub_type.capitalize()
            # A link to the doc for the TOC
            url_link =  f'[{Sub_type} {Report_type} - all data](/{reports_dir}/{reports_name}/{Sub_type}-{Report_type}.html)'
        else:
            sub_type = None
            Sub_type = None
            url_link =  f'[{Report_type} - all data](/{reports_dir}/{reports_name}/{Report_type}.html)'

        num_days = length.split(' ')[0]
        
        if sub_type not in self._fresh:
            # If the complete CSV data file has not been created, then create it
            self._fresh[sub_type] = True
            # This CSV file is used if the length of the report is 'all'
            self._gen_csv(report_type, sub_type, columns)
            
            # Generate a Github MD file for this data source
            original_length = report['length']
            report['length'] = 'all'
            self._gen_md(report)
            self._gen_js(report)
            report['length'] = original_length

            # A link to the new document for the TOC
            self._report_links.append(url_link)

        if length != 'all':
            if sub_type:
                self.log.debug(f"Generating {sub_type} {report_type} report with {length} of data")
            else:
                self.log.debug(f"Generating {report_type} report with {length} of data")
            # A link to the doc for the TOC
            if Sub_type:
                url_link = f"[{Sub_type} {Report_type} - {num_days} days](/{reports_dir}/{reports_name}/{Sub_type}-{Report_type}-{num_days}-Days.html)"
            else:
                url_link = f"[{Report_type} - {num_days} days](/{reports_dir}/{reports_name}/{Report_type}-{num_days}-Days.html)"
            # Create a shorter version of the CSV file, last 'length' days
            self._gen_csv_short(report)

            # Create a copy of the Javascript file with the updated filename
            self._gen_js(report)
            
        # Create a GitHub MD file using a template
        self._gen_md(report)
        # Create a link to the report for the TOC
        self._report_links.append(url_link)

    def _gen_csv(self, report_type, sub_type, columns):
        # Create a filename for the CSV file to be exported
        web_dir = self._web_dir
        csv_dir = self._csv_dir
        reports_name = self._yaml_file

        if sub_type:
            self.log.debug(f'Generating historical {sub_type} {report_type} report')
        else:
            self.log.debug(f'Generating historical {report_type} report')

        if sub_type == None:
            csv_filename = f"{report_type}.csv"
        else:
            csv_filename = f"{sub_type}-{report_type}.csv"

        csv_handle = open(os.path.join(web_dir, csv_dir, reports_name, csv_filename), 'w')

        # For the sharesfound reports, the columns depend on the list of currently active miners
        self._workers = []
        if report_type == 'sharesfound' and sub_type == 'by-miner':
            columns = 'Date,'
            db = MiningDb()
            workers = db.get_workers()
            for aWorker in workers.keys():
                if workers[aWorker]['active']:
                    self._workers.append(aWorker)
                    columns = columns + aWorker + ','
            columns = columns[:-1] # Chop off the trailing comma

        # Write the header to the CSV file
        csv_handle.write(columns + '\n')
        # Loop through the hashrate data and populate the CSV file
        report_data = self._get_data(report_type, sub_type)

        if report_type == 'hashrate':
            for row in report_data:
                # Get the timestamp and convert it to a date string
                timestamp = row['timestamp'] + ':00:00'
                # The hashrate data includes units (e.g. "6.889 KH/s")
                hashrate_value = row['hashrate'].split(' ')[0]
                csv_row = f"{timestamp},{hashrate_value}\n"
                csv_handle.write(csv_row)

        elif report_type == 'payment' and sub_type == 'daily':
            daily_payments = {}
            timestamps = []
            for row in report_data:
                timestamp = row['timestamp'].replace(hour=0, minute=0, second=0)
                payment = Decimal(row['payment'].to_decimal())
                # Aggregate the daily payouts
                if timestamp not in daily_payments:
                    daily_payments[timestamp] = payment
                else:
                    daily_payments[timestamp] += payment
                # Get a list of unique timestamps
                if timestamp not in timestamps:
                    timestamps.append(timestamp)
            timestamps.sort()
            for timestamp in timestamps:
                csv_row = f'{timestamp},{round(daily_payments[timestamp], 4)}\n'
                csv_handle.write(csv_row)

        elif report_type == 'payment' and sub_type == 'cumulative':
            daily_payments = {}
            timestamps = []
            for row in report_data:
                timestamp = row['timestamp'].replace(hour=0, minute=0, second=0)
                payment = Decimal(row['payment'].to_decimal())
                # Aggregate the daily payouts
                if timestamp not in daily_payments:
                    daily_payments[timestamp] = payment
                else:
                    daily_payments[timestamp] += payment
                # Get a list of unique timestamps
                if timestamp not in timestamps:
                    timestamps.append(timestamp)
            timestamps.sort()
            first_total = True
            for timestamp in timestamps:
                cur_pay = daily_payments[timestamp]
                if first_total == True:
                    first_total = False
                    cur_total = 0
                cur_total += cur_pay
                csv_row = f'{timestamp},{round(cur_total, 4)}\n'
                csv_handle.write(csv_row)

        elif report_type == 'blocksfound':
            daily_blocks = {}
            timestamps = []
            for row in report_data:
                timestamp = row['timestamp'].replace(hour=0, minute=0, second=0)
                # Aggregate the daily payouts
                if timestamp not in daily_blocks:
                    daily_blocks[timestamp] = 1
                else:
                    daily_blocks[timestamp] += 1
                # Get a list of unique timestamps
                if timestamp not in timestamps:
                    timestamps.append(timestamp)
            timestamps.sort()
            for timestamp in timestamps:
                csv_row = f'{timestamp},{daily_blocks[timestamp]}\n'
                csv_handle.write(csv_row)

        elif report_type == 'sharesfound' and sub_type == 'by-miner':
            daily_shares = {}
            timestamps = []
            worker_list= workers.keys()
            for row in report_data:
                timestamp = str(row['timestamp'].replace(hour=0, minute=0, second=0))
                # Aggregate the daily payouts
                if timestamp not in daily_shares:
                    daily_shares[timestamp] = {}
                worker = row['worker']
                if worker not in daily_shares[timestamp]:
                    daily_shares[timestamp][worker] = 1
                else:
                    daily_shares[timestamp][worker] += 1
                if timestamp not in timestamps:
                    timestamps.append(timestamp)
            timestamps.sort()
            for timestamp in timestamps:
                csv_row = timestamp + ','
                for aMiner in worker_list:
                    if aMiner in daily_shares[timestamp]:
                        csv_row += str(daily_shares[timestamp][aMiner]) + ','
                    else:
                        csv_row += '0,'
                csv_row = csv_row[:-1] + '\n' # Chop off trailing comma
                csv_handle.write(csv_row)

        elif report_type == 'sharesfound':
            daily_shares = {}
            timestamps = []
            for row in report_data:
                timestamp = row['timestamp'].replace(hour=0, minute=0)
                # Aggregate the daily payouts
                if timestamp not in daily_shares:
                    daily_shares[timestamp] = 1
                else:
                    daily_shares[timestamp] += 1
                # Get a list of unique timestamps
                if timestamp not in timestamps:
                    timestamps.append(timestamp)
            timestamps.sort()
            for timestamp in timestamps:
                csv_row = f'{timestamp},{daily_shares[timestamp]}\n'
                csv_handle.write(csv_row)


        csv_handle.close()
        export_file = os.path.join(web_dir, csv_dir, reports_name, csv_filename)
        self.log.debug(f"Created CSV file ({export_file})", 
                      {'new_file': export_file, 'file_type': 'csv'})
        self.git.add(export_file)

    def _gen_csv_short(self, report):
        # Create a shorter version of the CSV file, last 'length' days
        web_dir  = self._web_dir
        csv_dir      = self._csv_dir
        reports_name = self._yaml_file
        report_type  = report['report_type']
        length       = report['length']
        num_days = length.split(' ')[0]
        if 'sub_type' in report:
            sub_type = report['sub_type']
            in_file = f"{sub_type}-{report_type}.csv"
            out_file = f"{sub_type}-{report_type}-{num_days}days.csv"
        else:
            sub_type = None
            in_file = f"{report_type}.csv"
            out_file = f"{report_type}-{num_days}days.csv"


        in_handle = open(os.path.join(web_dir, csv_dir, reports_name, in_file), 'r')
        out_handle = open(os.path.join(web_dir, csv_dir, reports_name, out_file), 'w')
        
        if report_type == 'hashrate':
            # The hashrate data is hourly
            rows = int(num_days) * 24
        elif report_type == 'payment' or report_type == 'blocksfound' or report_type == 'sharesfound':
            # The payment and blocksfound data is daily
            rows = int(num_days)

        # Read and Write
        in_lines = in_handle.readlines()
        out_handle.write(in_lines[0])  # Write the header line
        # Get the last 'rows' rows from the long file
        for line in in_lines[-rows:]:
            out_handle.write(line)
        # Close the files, print some output and issue a 'git add <file>'
        out_handle.close()
        in_handle.close()
        export_file = os.path.join(web_dir, csv_dir, reports_name, out_file)
        self.git.add(export_file)
        self.log.debug(f"Created CSV file ({export_file})", 
                      {'new_file': export_file, 'file_type': 'csv'})
        
    def _gen_js(self, report):
        # Create a copy of the Javascript file with the updated filename
        db4e_dir     = self._db4e_dir
        web_dir      = self._web_dir
        tmpl_dir     = self._templates_dir
        js_dir       = self._js_dir
        reports_name = self._yaml_file
        report_type  = report['report_type']
        length       = report['length']
        num_days = length.split(' ')[0]

        if 'sub_type' not in report:
            sub_type = None
            in_file = f"{report_type}.js"
            if length == 'all':
                out_file = f"{report_type}.js"
            else:
                out_file = f"{report_type}-{num_days}days.js"
        else:
            sub_type = report['sub_type']
            in_file = f"{sub_type}-{report_type}.js"
            if length == 'all':
                out_file = f"{sub_type}-{report_type}.js"
            else:
                out_file = f"{sub_type}-{report_type}-{num_days}days.js"

        in_handle = open(os.path.join(db4e_dir, tmpl_dir, js_dir, in_file), 'r')
        out_handle = open(os.path.join(web_dir, js_dir, reports_name, out_file), 'w')

        in_lines = in_handle.readlines()
        if sub_type == None:
            old_csv = f"{report_type}.csv"
            if length == 'all':
                new_csv = f"{reports_name}/{report_type}.csv"
            else:
                new_csv = f"{reports_name}/{report_type}-{num_days}days.csv"
        else:
            old_csv = f"{sub_type}-{report_type}.csv"
            if length == 'all':
                new_csv = f"{reports_name}/{sub_type}-{report_type}.csv"
            else:
                new_csv = f"{reports_name}/{sub_type}-{report_type}-{num_days}days.csv"

        for line in in_lines:
            # Read and Write....
            line = line.replace(old_csv, new_csv)
            if report_type == 'sharesfound' and sub_type == 'by-miner':
                if line == '[[CONST_TOTAL_MINER_DEFS]]\n':
                    for worker in self._workers:
                        js_line = f'const total{worker.capitalize()}Data = [];\n'
                        out_handle.write(js_line)
                elif line == '[[CONST_MINER_DEFS]]\n':
                    for worker in self._workers:
                        js_line = f"const {worker} = row['{worker}'];\n"
                        out_handle.write(js_line)
                elif line == '[[TOTAL_MINER_PUSH]]\n':
                    for worker in self._workers:
                        js_line = f'total{worker.capitalize()}Data.push(' + '{ x:date, y: ' + worker + '});\n'
                        out_handle.write('      ' + js_line)
                elif line == '[[SERIES_DEFS]]\n':
                    for worker in self._workers:
                        out_handle.write('        {\n')
                        out_handle.write(f'          name: "{worker.capitalize()}",\n')
                        out_handle.write(f'          data: total{worker.capitalize()}Data\n')
                        out_handle.write('        },\n')
                else:
                    out_handle.write(line)
            else:
                out_handle.write(line)
                
        # Close out nicely
        out_handle.close()
        in_handle.close()
        export_file = os.path.join(web_dir, js_dir, reports_name, out_file)
        self.git.add(export_file)
        self.log.debug(f"Created JavaScript file ({export_file})", 
                      {'new_file': export_file, 'file_type': 'js'})

    def _gen_md(self, report):
        # Generate a Github MD file for the new report
        reports_name  = self._yaml_file
        report_type   = report['report_type']
        title         = report['title']
        length        = report['length']
        if 'sub_type' in report:
            sub_type = report['sub_type']
            Sub_type = sub_type.capitalize()
        else:
            sub_type = None
            Sub_type = None

        db4e_dir      = self._db4e_dir
        web_dir       = self._web_dir
        templates_dir = self._templates_dir
        reports_dir   = self._reports_dir
        md_dir        = self._md_dir

        num_days = length.split(' ')[0]
        Report_type = report_type.capitalize()

        in_file = f"{sub_type}-{report_type}.tmpl"

        if Sub_type == None:
            # blocksfound reports do not have a sub_type
            in_file = f'{report_type}.tmpl'
            if length == 'all':
                out_file = f'{Report_type}.md'
            else:
                out_file = f'{Report_type}-{num_days}-Days.md'
        
        else:
            # hashrates and payments reports both have a sub_type
            in_file = f"{sub_type}-{report_type}.tmpl"
            if length == 'all':
                out_file = f'{Sub_type}-{Report_type}.md'
            else:
                out_file = f'{Sub_type}-{Report_type}-{num_days}-Days.md'

        in_handle = open(os.path.join(db4e_dir, templates_dir, md_dir, report_type, in_file), 'r')
        out_handle = open(os.path.join(web_dir, reports_dir, reports_name, out_file), 'w')

        # Generate a JavaScript filename
        if Sub_type == None:
            if length == 'all':
                js_file = f"{report_type}.js"
            else:
                js_file = f"{report_type}-{num_days}days.js"
        else:
            if length == 'all':
                js_file = f"{sub_type}-{report_type}.js"
            else:
                js_file = f"{sub_type}-{report_type}-{num_days}days.js"
            
        # Generate the GitHub Markdown header
        out_handle.write('---\n')
        out_handle.write(f'title: {title}\n')
        date_str = datetime.now().strftime("%Y-%m-%d")
        out_handle.write(f'date: {date_str}\n')
        out_handle.write('---\n\n')
        
        # Read in the template file
        in_lines = in_handle.readlines()
        
        # Update the reference to the javascript code
        if sub_type == None:
            old_js = f'{report_type}.js'
            if length == 'all':
                new_js = f'{reports_name}/{report_type}.js'
            else:
                new_js = f'{reports_name}/{report_type}-{num_days}days.js'
        else:
            old_js = f'{sub_type}-{report_type}.js'
            if length == 'all':
                new_js = f'{reports_name}/{sub_type}-{report_type}.js'
            else:
                new_js = f'{reports_name}/{sub_type}-{report_type}-{num_days}days.js'

        for line in in_lines:
            line = line.replace(old_js, new_js)
            out_handle.write(line)

        if length == 'all':
            out_handle.write(f'* Days of data: all available\n')
        else:
            out_handle.write(f'* Days of data: {num_days}\n')
        datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        out_handle.write(f'* Last updated: {datetime_str}\n')

        # Clean exit....
        out_handle.close()
        in_handle.close()
        export_file = os.path.join(web_dir, reports_dir, reports_name, out_file)
        self.git.add(export_file)
        self.log.debug(f"Created GitHub markdown file ({export_file})", 
                      {'new_file': export_file, 'file_type': 'md'})


    def _gen_toc(self, report_type):
        reports_name = self._yaml_file
        Report_type  = report_type.capitalize()
        web_dir      = self._web_dir
        reports_dir  = self._reports_dir
        conf_dir     = self._conf_dir
        toc_file     = 'index.md'

        toc_handle = open(os.path.join(web_dir, reports_dir, reports_name, toc_file), 'w')
        # Generate the GitHub Markdown header
        toc_handle.write('---\n')
        toc_handle.write(f'title: {Report_type} Reports\n')
        date_str = datetime.now().strftime("%Y-%m-%d")
        toc_handle.write(f'date: {date_str}\n')
        toc_handle.write('---\n\n')
        toc_handle.write("# Reports\n\n")
        for link in self._report_links:
            toc_handle.write(f'* {link}\n')
        datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        toc_handle.write(f'\nLast updated: {datetime_str}\n')
        toc_handle.close()
        export_file = os.path.join(web_dir, reports_dir, reports_name, toc_file)
        self.git.add(export_file)
        self.log.debug(f"Created reports summary GitHub markdown file ({export_file})", 
                      {'new_file': export_file, 'file_type': 'md'})
        
    def _get_data(self, report_type, sub_type):
        # Get the latest data from the MiningDb
        db = MiningDb()
        doc_name = None
        if report_type == 'hashrate':
            doc_name = f"{sub_type}_{report_type}"
        elif report_type == 'payment':
            doc_name = 'xmr_payment'
        elif report_type == 'blocksfound':
            doc_name = 'block_found_event'
        elif report_type == 'sharesfound':
            doc_name = 'share_found_event'
        else:
            self.log.critical(f'ERROR: Unknown report type {report_type}')
        return db.get_docs(doc_name)

    def _load_reports(self):
        # Report files are in conf/reports
        db4e_dir = self._db4e_dir
        conf_dir = self._conf_dir
        reports_dir = self._reports_dir
        yaml_file = f'{self._yaml_file}.yml'
        # E.g. db4e/conf/reports/hashrates.yml
        report_file = os.path.join(db4e_dir, conf_dir, reports_dir, yaml_file)        
        with open(os.path.join(report_file), 'r') as file:
            self._reports = yaml.safe_load(file)
        self._report_file = report_file


    
