import random

import subprocess
import os
import time

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, Button, Log, Static

TEST_SCRIPT = "/tmp/sudo_test.sh"
SUDO = "/usr/bin/sudo"


class SudoHandlerApp(App):

    password_requested = None

    def compose(self) -> ComposeResult:

        yield Button("Start Test", id="STARTTEST")
        yield Log(id="LOG")
        yield Input("Enter your account password: ", id="USERPASS")
        yield Button("Follow Up", id="FOLLOWUP")

    def on_button_pressed(self, event: Button.Pressed):
        button_id = event.button.id

        # Log widget
        log = self.query_one(f"#LOG", Log)

        if button_id == "STARTTEST":
            self.do_sudo_test()
            if self.password_requested == False:
                log.write_line("User has sudo password free sudo access")
            elif self.password_requested == True:
                log.write_line("Password is being requested")

        elif button_id == "FOLLOWUP":
            process = subprocess.Popen(
                [SUDO, TEST_SCRIPT],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            user_password = self.query_one(f"#USERPASS").value
            time.sleep(1)
            stdout, stderr = process.communicate(input=user_password + "\n")

            log.write_line(f"Follow Up return code: {process.returncode}")

    def do_sudo_test(self) -> None:
        # Log widget
        log = self.query_one(f"#LOG", Log)

        # Create the test file
        with open(TEST_SCRIPT, "w") as file:
            file.write(
                "#!/bin/bash\n\n"
                "TEST_FILE=/tmp/foo\n"
                "touch $TEST_FILE\n"
                'echo "Created test file: $TEST_FILE"\n'
                "ls - $TEST_FILE\n"
            )
        log.write_line(f"Created test script {TEST_SCRIPT}")

        # Make the test script exectable
        os.chmod(TEST_SCRIPT, 0o755)
        log.write_line("Flagged script as executible")

        try:
            log.write_line("Preparing to run script...")
            result = subprocess.run(
                [SUDO, TEST_SCRIPT],
                timeout=1,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            log.write_line(f"Return code was: {result.returncode}")
            self.password_requested = False

        except subprocess.TimeoutExpired:
            log.write_line(f"Script timed out waiting for sudo password")
            self.password_requested = True

        finally:
            pass


if __name__ == "__main__":
    app = SudoHandlerApp()
    app.run()
