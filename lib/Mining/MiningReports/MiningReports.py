"""
Mining/MiningReports/MiningReports.py
"""

import yaml
import os, sys
from datetime import datetime
import shutil

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

class MiningReports():
  
    def __init__(self, log_func=None):
        # Set up the logger function
        self.log = log_func

        # Load the configuration 
        config = Db4eConfig()
        self._install_dir = config.config['db4e']['install_dir']
        self._conf_dir = config.config['db4e']['conf_dir']
        self._js_dir = config.config['db4e']['js_dir']
        self._csv_dir = config.config['export']['csv_dir']
        self._yaml_file = config.config['export']['reports']
        self._templates_dir = config.config['export']['template_dir']
        self._reports_dir = config.config['export']['reports_dir']
        
        # Load the report definitions from the YAML file
        self._load_reports()

        # Define some state information
        self._fresh = {}
        self._fresh['pool'] = False
        self._fresh['sidechain'] = False
        self._fresh['mainchain'] = False

        # Get a db4e Git object
        self.git = Db4eGit(self._install_dir)

        # We'll create a reports summary page as well
        self._report_links = []

        # Clean out any old CSV files, reports and the old table of contents
        shutil.rmtree(self._csv_dir)
        shutil.rmtree(self._reports_dir)

    def run(self):
        """
        Run the mining reports based on the loaded configuration.
        This method should be implemented to generate the reports.
        """
        install_dir = self._install_dir
        csv_dir = self._csv_dir
        js_dir = self._js_dir
        templates_dir = self._templates_dir
        reports_dir = self._reports_dir

        self._load_reports()

        for report in self._reports:
            report_type = report['report_type']
            Report_type = report_type.capitalize()
            sub_type = report['sub_type']
            Sub_type = sub_type.capitalize()
            title = report['title']
            units = report['units']
            length = report['length']
            columns = report.get('columns', None)

            print(f"Generating report: {report_type} - {sub_type} - {length}")
            url_link =  f"[{Sub_type} {Report_type}](/{reports_dir}/{Sub_type}-{Report_type}.html)"


            if not self._fresh[sub_type]:
                # If the complete chain CSV data file has not been created, then create it
                self._fresh[sub_type] = True
                # This CSV file is used if the length of the report is 'all'
                self._gen_csv(report_type, sub_type, columns)
                self._report_links.append(url_link)

            if length != 'all':
                num_days = length.split(' ')[0]
                url_link = f"[{Sub_type} {Report_type} - {num_days} days](/{reports_dir}/{Sub_type}-{Report_type}-{num_days}-Days.html)"
                # Create a shorter version of the CSV file, last 'length' days
                in_file = f"{sub_type}-{report_type}.csv"
                rows = int(num_days) * 24 # The data contains one row per hour
                out_file = f"{sub_type}-{report_type}-{num_days}days.csv"
                out_handle = open(os.path.join(install_dir, csv_dir, out_file), 'w')
                in_handle = open(os.path.join(install_dir, csv_dir, in_file), 'r')
                in_lines = in_handle.readlines()
                out_handle.write(in_lines[0])  # Write the header line
                # Get the last 'rows' rows from the long file
                for line in in_lines[-rows:]:
                    out_handle.write(line)
                out_handle.close()
                in_handle.close()
                print(f"  Exported: {os.path.join(install_dir, csv_dir, out_file)}")
                self.git.add(os.path.join(csv_dir, out_file))
                
                # Create a copy of the Javascript file with the updated filename
                in_file = f"{sub_type}-{report_type}.js"
                out_file = f"{sub_type}-{report_type}-{num_days}days.js"
                in_handle = open(os.path.join(install_dir, js_dir, in_file), 'r')
                out_handle = open(os.path.join(install_dir, js_dir, out_file), 'w')
                in_lines = in_handle.readlines()
                old_csv = f"{sub_type}-{report_type}.csv"
                new_csv = f"{sub_type}-{report_type}-{num_days}days.csv"
                for line in in_lines:
                    line = line.replace(old_csv, new_csv)
                    out_handle.write(line)
                out_handle.close()
                in_handle.close()
                print(f"  Exported: {os.path.join(install_dir, js_dir,out_file)}")
                self.git.add(os.path.join(js_dir, out_file))

            # Create a GitHub MD file using a template
            in_file = f"{sub_type}-{report_type}.tmpl"
            if length == 'all':
                out_file = f"{Sub_type}-{Report_type}.md"
            else:
                out_file = f"{Sub_type}-{Report_type}-{num_days}-Days.md"
            in_handle = open(os.path.join(install_dir, templates_dir, in_file), 'r')
            if not os.path.exists(os.path.join(install_dir, reports_dir)):
                os.mkdir(os.path.join(install_dir, reports_dir))
            out_handle = open(os.path.join(install_dir, reports_dir, out_file), 'w')

            # Generate a JavaScript filename
            if length == 'all':
                js_file = f"{sub_type}-{report_type}.js"
            else:
                js_file = f"{sub_type}-{report_type}-{num_days}days.js"
                
            # Generate the GitHub Markdown header
            out_handle.write('---\n')
            out_handle.write('layout: post\n')
            out_handle.write(f'title: {title}\n')
            date_str = datetime.now().strftime("%Y-%m-%d")
            out_handle.write(f'date: {date_str}\n')
            out_handle.write('---\n\n')
            datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            out_handle.write(f'Last updated: {datetime_str}\n')

            # Read in the template file
            in_lines = in_handle.readlines()
            # Write it to the new output file
            if length != 'all':
                # We need to replace the Javascript target
                old_js = f"{sub_type}-{report_type}.js"
                new_js = f"{sub_type}-{report_type}-{num_days}days.js"
            for line in in_lines:
                line = line.replace(old_js, new_js)
                out_handle.write(line)
            # Clean exit....
            out_handle.close()
            in_handle.close()
            print(f"  Exported: {os.path.join(install_dir, reports_dir, out_file)}")
            self.git.add(os.path.join(reports_dir, out_file))
            self._report_links.append(url_link)
            print("-" * 40)

        # Generate a list of reports on a Github MD page
        self._gen_toc()

        print("Pushing reports to GitHub: ", end='')
        self.git.commit("New reports")
        self.git.push()
        print("Done")


    def _gen_csv(self, report_type, sub_type, columns):
        print(f"  Generating historical report: {report_type} - {sub_type}")
        # Create a filename for the CSV file to be exported
        install_dir = self._install_dir
        csv_dir = self._csv_dir

        csv_filename = f"{sub_type}-{report_type}.csv"
        if not os.path.exists(os.path.join(install_dir,csv_dir)):
            os.mkdir(os.path.join(install_dir, csv_dir))
            
        csv_handle = open(os.path.join(install_dir, csv_dir, csv_filename), 'w')

        # Write the header to the CSV file
        csv_handle.write(columns + '\n')
        # Loop through the hashrate data and populate the CSV file
        report_data = self._get_data(report_type, sub_type)

        if report_type == 'hashrate':
            for row in report_data:
                # Get the timestamp and convert it to a date string
                timestamp = row['timestamp'] + ':00:00'
                # The hashrate data is in KH/s (e.g. "6.889 KH/s")
                hashrate_value = row['hashrate'].split(' ')[0]
                csv_row = f"{timestamp},{hashrate_value}\n"
                csv_handle.write(csv_row)
            csv_handle.close()
            print(f"  Exported: {os.path.join(install_dir, csv_dir, csv_filename)}")
            self.git.add(os.path.join(csv_dir, csv_filename))

    def _gen_toc(self):
        install_dir = self._install_dir
        reports_dir = self._reports_dir
        toc_file = 'index.md'
        toc_handle = open(os.path.join(install_dir, reports_dir, toc_file), 'w')
        # Generate the GitHub Markdown header
        toc_handle.write('---\n')
        toc_handle.write('layout: post\n')
        toc_handle.write(f'title: Reports\n')
        date_str = datetime.now().strftime("%Y-%m-%d")
        toc_handle.write(f'date: {date_str}\n')
        toc_handle.write('---\n\n')
        for link in self._report_links:
            toc_handle.write(f'* {link}\n')
        self.git.add(os.path.join(install_dir, reports_dir, toc_file))
        datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        toc_handle.write(f'\nLast updated: {datetime_str}\n')
        toc_handle.close()
        self.git.add(os.path.join(install_dir, reports_dir, toc_file))
        print(f"  Exported: {os.path.join(install_dir, reports_dir, toc_file)}")


    def _load_reports(self):
        yaml_file = os.path.join(self._install_dir, self._conf_dir, self._yaml_file)
        with open(yaml_file, 'r') as file:
            self._reports = yaml.safe_load(file)

    def _get_data(self, report_type, sub_type):
        # Get the latest data from the MiningDb
        db = MiningDb()
        doc_name = f"{sub_type}_{report_type}"
        return db.get_docs(doc_name)

    