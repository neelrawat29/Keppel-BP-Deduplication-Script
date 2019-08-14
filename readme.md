# Excel de-duplication script

A simple script used to find potential duplicates. Requires Python 3. 64-bit will probably help if running on larger files. 

## Installation

Create a virtual environment, update pip, and install requirements.

```bash
python -m venv .
.\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r .\requirements.txt
```

## To-do

* Rewrite script to be less garbage (since the requirements changed several time, the current method is really quite inefficient)
* Add a sample input file (and tests?)
