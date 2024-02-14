# Zabbix Template Exporter

This Python script is used to export Zabbix templates from a Zabbix server and push them to a local git repository.

## Prerequisites

- Python 3.x
- Git
- Zabbix server access
- API key for Zabbix server

## Installation

1. Clone the repository:

   ```sh
   git clone <repository_url>
   ```

2. Install the required Python packages:

   ```sh
   pip install requests
   ```

3. Configure the script by setting the following variables:

- ZABBIX_API_URL: URL of the Zabbix server API
- AUTH: API key for accessing the Zabbix server
- SELECTED_TEMPLATES_GROUPID: Group ID of the selected templates in Zabbix
- PATH_TO_LOCAL_GIT_REPO: Path to the local git repository
- GIT_PUSH: Boolean to enable/disable pushing changes to the git repository

## Usage

Run the script:

```sh
python zabbix_template_export.py
```
