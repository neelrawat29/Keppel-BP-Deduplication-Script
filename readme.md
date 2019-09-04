# Excel de-duplication script

A simple script used to find potential duplicates. Requires Python 3. 64-bit will probably help if running on larger files. 

## Installation

Create a virtual environment, update pip, and install requirements.

```PowerShell
python -m venv .
.\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r .\requirements.txt
```

## Usage

```PowerShell
.\Scripts\Activate.ps1
python .\dedup.py path\to\file.xlsx
```

## To-do

* Rewrite script to be less garbage (since the requirements changed several time, the current method is really quite inefficient)
* Add a sample input file (and tests?)
