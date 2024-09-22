# musestore-migrate

Scripts for migrating a `.csv` file to the musestore database by generating insert statements.

Compatible with musestore `v0.1.0`.

> [!IMPORTANT]
>
> * Make sure the tables have been created beforehand.
> * Always create a backup of your database before running the insert statements.
> * There are no checks for SQL injections. Only use trusted input files. Check output before running it.
> * When using a release, make sure you read its README. It could be different from the last commit.

## Options

Flag | Action
--- | ---
`--convert-path` | Change all backward slashes to forward slashes in filepaths.
`--skip-file-processing` | Do not process files listed in the csv file. Useful when debugging.

## Input format

### Columns

Column name | Constraints | Process | Required
--- | --- | --- | ---
ID | positive integer | Entries with duplicate IDs are ignored. | <span style="color:red">false</span>
Name | 255 chars | Entries with the same name are grouped together. A piece is created for every unique name. A new item is created for every new entry. | <span style="color:green">true</span>
Composer | 255 chars | Tags are created for new composers. Tags are added to the specified piece. | <span style="color:red">false</span>
Instrument | 255 chars for every instrument | Tags are created for new instruments. Multiple instruments can be assigned with a `/`. Tags are added to the specified piece. | <span style="color:red">false</span>
Grade | 255 chars | Tags are created for new instruments. Tags are added to the specified piece. | <span style="color:red">false</span>
Type | 255 chars | Types are created for new entries. Required if there is a file. | <span style="color:red">false</span> (no file)
File | filepath | Files are copied to the output directory. | <span style="color:red">false</span>

### Example

ID | Name | Composer | Instrument | Grade | Scale | Type | File
--- | --- | --- | --- | --- | --- | --- | ---
1 | Tico-Tico no Fubá | Abreu Zequinha | flute | 6 | d-moll | Partiture | Abreu Zequinha\Abreu_Tico_tico_Flute.pdf
2 | Tico-Tico no Fubá | Abreu Zequinha | flute/piano | 6 | d-moll | Partiture | Abreu Zequinha\Abreu_Tico_tico_complete.pdf
3 | Le Basque | Marin Marais | flute | 5 | F-dur | Partiture | Marais Marin\Marais_Le Basque_flute.pdf

## Instructions

### Linux

* Download the latest release (stable)
	* Or clone this repository (unstable) `git clone https://github.com/tgrants/musestore-migrate`
* Create a virtual environment `python3 -m venv venv`
* Activate the virtual environment `source ./venv/bin/activate`
* Install all dependencies `pip install -r requirements.txt`
* Run with a path to a correctly formatted .csv file `python3 import.py ./input/db.csv`

### Windows

## Other information

### Versioning and compatibility

* Major version - same as musestore
* Minor version - incremented by one after updates. See the compatibility table below.

Musestore-migrate | Musestore
--- | ---
0.1 | 0.1.0

### License

This repository is licensed under the MIT License. See `LICENSE` for more information.
