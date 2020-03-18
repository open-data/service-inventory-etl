# Service Inventory Data Transformation
This project takes a flat Excel extract from Titan, transforms it into a CSV format that conforms to the published YAML schema, and publishes it to the Open Data registry.

## Project Setup
1. This is a Python project.  For it to run, you must have [Python installed](https://www.python.org/downloads/) on your system.
1. Once Python is installed, open Powershell/Git Bash/Terminal and change to the directory where you'd like to keep this code base (e.g. `cd C:\Code`).
1. Install Python Virtual Environments
    * `pip install virtualenv`
1. Use git to clone this repository
    * `git clone <url_of_the_repository> <local_directory_name>`
1. Create and activate a virtual environment
    * `cd <local_directory_name>`
    * `virtualenv venv`
    * `venv/Scripts/activate`
        * On MacOS and Linux you'll need to run `source venv/Scripts/activate`
* Once you've activatated the virtual environment, Install the project requirements
    * `pip install -r requirements.txt`
* Open your favourite text editor and create a `configuration.json` file with the required settings.
    * Take a copy of `configuration.template.json` and just change the values leaving the structure in tact.


## Running the Program
1. From the command line of your choice in the project directory, run this to start running the program
    * `python main.py`

## Project Files

### main .py
The main program file that calls all other functions to execute various parts of the transformation.  The majority of the settings are managed in this file with the exception of sensitive information.

### configuration.template.json
A template to guide you to the creation of your own **configuration.json** file.

### build_json_from_yaml.py
Retrieves the YAML schema from GitHub and converts it to a JSON Table Schema.

### parse_titan_flat_extract.py
Loads the flat extract Excel file from Titan and produces a CSV in the desired format.

### validate_csv_quality.py
Runs the generated CSV through a series of data quality checks

### prep_and_publish_data.py
Converts the CSV to JSON format expected by the Service Inventory component in the CKAN registry and publishes the new data using the registry API.

