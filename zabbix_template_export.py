#!/usr/bin/python3
import json
import os
import xml.dom.minidom
from os.path import join as pjoin
from typing import Literal, Optional, Any  # from typing_extensions import Literal # Python 3.7 or below

import requests
import subprocess

ZABBIX_API_URL = "https://<YOUR_ZABBIX_SERVER>/api_jsonrpc.php"
AUTH = "<YOUR_API_KEY>"
SELECTED_TEMPLATES_GROUPID = "<SELECTED_TEMPLATES_GROUPID>"
PATH_TO_LOCAL_GIT_REPO = "<PATH_TO_LOCAL_GIT_REPO>"
GIT_PUSH = True

class ZabbixClient:
    """Zabbix client API"""

    def __init__(self, url, auth):
        self.url = url
        self.auth = auth

    def request(self, method: str, params: Any, timeout: float = 60) -> dict:
        """Send an API request and return the response (as requests response)."""
        r = requests.post(
            self.url,
            json={"jsonrpc": "2.0", "method": method, "params": params, "auth": self.auth, "id": 1},
            headers={"content-type": "application/json"},
            timeout=timeout,
        )
        result = r.json()
        assert isinstance(result, dict), "The API returns a dictionary."
        return result

    def export_template(self, id_: str, file_name: str = None, output_path: Optional[str] = None,
                        output_format: Literal['xml', 'json'] = "xml"):
        """Export a Zabbix template in XML format and save it to a file."""
        # Make a POST request to the Zabbix API to export the template in XML format
        result = self.request(method="configuration.export",
                              params={"options": {"templates": [id_]}, "format": output_format})

        # Define the destination file path for the exported XML template
        if not file_name:
            file_name = id_

        if output_path:
            try:
                os.mkdir(output_path)
            except FileExistsError:
                pass

            output_file_path = pjoin(output_path, f"{file_name}.{output_format}")
        else:
            output_file_path = f"{file_name}.{output_format}"

        # Save the content to a file.
        if output_format == "xml":
            dom = xml.dom.minidom.parseString(result["result"])
            pretty_xml = dom.toprettyxml()
            with open(output_file_path, "w", encoding="utf-8") as out_file:
                out_file.write(pretty_xml)
        elif output_format == "json":
            result = json.dumps(json.loads(result["result"]), indent=4, sort_keys=True)
            with open(output_file_path, "w", encoding="utf-8") as out_file:
                out_file.write(result)
        else:
            raise NotImplementedError("Only XML and JSON formats are supported")

        # Print a success message
        print(f"Template {file_name} exported to {output_file_path!r}")

    def get_zabbix_templates(self, group_id: int) -> dict[str, str]:
        """Get all Zabbix templates using the Zabbix API"""
        # Make a POST request to the Zabbix API
        result = self.request(method="template.get", params={"output": ["host"], "groupids": group_id})

        # Return a dictionary of id to name of Zabbix templates
        return {item["templateid"]: item["host"] for item in result["result"]}


class GitRepoManager:
    """A class for managing a git repository"""

    def __init__(self, repo_path):
        self.repo_path = repo_path


    def add_and_commit(self, file_path: str, commit_message: str):
        """Add the file to the git repo and commit it with the given message"""
        os.system(f"git -C \"{self.repo_path}\" add \"{file_path}\"")
        if subprocess.call(f"git -C \"{self.repo_path}\" diff --cached --quiet", shell=True) != 0:
            os.system(f"git -C \"{self.repo_path}\" commit -m \"{commit_message}\"")
            os.system(f"git -C \"{self.repo_path}\" push")
        else:
            print("No changes staged for commit")


def main():
    """The main and only function here."""
    api = ZabbixClient(ZABBIX_API_URL, AUTH)
    templates = api.get_zabbix_templates(group_id=SELECTED_TEMPLATES_GROUPID)
    for id_, name in templates.items():
        api.export_template(id_=id_, file_name=name, output_format="json", output_path="zabbix_templates")

    # Push the downloaded files to a git repo
    git_manager = GitRepoManager(repo_path=PATH_TO_LOCAL_GIT_REPO)
    if GIT_PUSH:
        git_manager.add_and_commit(file_path="zabbix_templates/*", commit_message="Update Zabbix templates")


if __name__ == "__main__":
    main()
