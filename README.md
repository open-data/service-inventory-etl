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
* Set the value for `environment` in the `/main.py` file to point to the environment you would like to publish to (i.e. staging or production)

## Running the Program
1. Put the latest extract file into the `/data/` folder and name it `latest_annual_extract.xlsx`
    * **NOTE:** The program expects the extract to contain a *single* `fiscal_yr` (e.g. 2018-2019) and will exit with an error if multiple years are found in the same file.
1. From the command line of your choice in the project directory, run this to start running the program
    * `python main.py`
1. The program will transform the new extract into the schema defined by the YAML and then validate the resulting data to ensure compliance and overall quality.  The output of the processing will be stored in the `/data/yearly/` folder with `fiscal_year` as a prefix (e.g. /data/yearly/2018-2019_services.csv)
1. The program will then merge together all files of a particular type (i.e. services or standards) and revalidate for compliance and overall quality.
1. Finally, the merged files for both services and standards will be published to the portal.
    * Publishing will only happen if the --publish command-line argument is suplied.  More details in the Command-line Options section below.

### Command-line Options
By default, this script will activate the staging environment as the target and disable publishing.  You can override this default behaviour by using the following command-line arguments:

    --p, --publish:     Enable publishing on this run
        default: False
    --e, --environment: Specify the environment to publish to
        choices: {staging, production}
        default: staging

Examples:
```
# Default - Target staging and don't publish
python main.py

# Comand-line Help
python main.py --help

# Explicitly target staging and publish
python main.py --environment staging --publish

# Target production and publish (verbose)
python main.py --environment production --publish

# Target production and publish
python main.py --e production --p
```


## Historic Data
There is a helper script in the root folder called `historic_data_quality_check.py` which will incorporate older historic data into the overall merge process.  If the historic (2016-2017 or 2017-2018) data needs to be updated, replace `/data/historic/historic_data.xlsx` with an updated file and run `python historic_data_quality_check.py` to regenerate the files needed by the merge component.

## Data Quality Errors
This script will abort if any data quality checks fail.  When a validation error is encountered, a full report will be written to `/errors/` with all of the details needed to correct the problem(s).  Correct the issues in the source dataset file and run the script again.

## Backing Up
Once a new year is all merged and published, clear the `/errors/` folder and commit the changes to git.  The following commands entered into terminal/gitbash will allow you to commit and push your changes to the repository:
* `cd <local_directory_name>`
* `git add .`
* `git commit -m "Enter a commit message (e.g. Updating files for 2018-2019)"`
* `git push origin master`

