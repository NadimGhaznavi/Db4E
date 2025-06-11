import urwid
import subprocess
import os
import shutil

class Db4eRepoSetupUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self.repo_name_edit = urwid.Edit("GitHub repo name (e.g. NadimGhaznavi/xmr): ")
        self.repo_path_edit = urwid.Edit("Local path to clone repo: ")
        self.info_text = urwid.Text("")
        self.form = urwid.Pile([
            self.repo_name_edit,
            self.repo_path_edit,
            urwid.Button("Submit", on_press=self.on_submit),
            urwid.Button("Back", on_press=self.back_to_main)
        ])
        self.frame = urwid.LineBox(
            urwid.Padding(urwid.Pile([self.form, self.info_text]), left=2, right=2),
            title="GitHub Repo Setup", title_align="center", title_attr="title"
        )

    def back_to_main(self, button):
        self.parent_tui.return_to_main()

    def on_submit(self, button):
        repo_name = self.repo_name_edit.edit_text.strip()
        clone_path = os.path.expanduser(self.repo_path_edit.edit_text.strip())

        # Validate input
        if not repo_name or not clone_path:
            self.info_text.set_text("Please provide both the repository name and clone path.")
            return

        # Check SSH access
        try:
            ssh_result = subprocess.run(
                ["ssh", "-T", "git@github.com"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                input=b"",
                timeout=10
            )
            if ssh_result.returncode not in (0, 1):  # 1 is acceptable for SSH auth check
                self.info_text.set_text("SSH connection failed. Ensure SSH is configured for GitHub.")
                return
        except Exception as e:
            self.info_text.set_text(f"SSH check failed: {str(e)}")
            return

        # Try to clone
        try:
            if os.path.exists(clone_path):
                shutil.rmtree(clone_path)
            subprocess.run([
                "git", "clone", f"git@github.com:{repo_name}.git", clone_path
            ], check=True)
            self.info_text.set_text("Repository cloned successfully.")
        except subprocess.CalledProcessError:
            self.info_text.set_text("Failed to clone the repository. Check SSH and repo name.")
        except Exception as e:
            self.info_text.set_text(f"Error: {str(e)}")

    def widget(self):
        return self.frame
