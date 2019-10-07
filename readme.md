# Excel de-duplication script

One-time script for finding duplicates via fuzzy matching, created for data migration in some project. Putting it here in case I find a use for it some other time.

Requires Python 3. 64-bit will probably help if running on larger files.  

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
python .\dedupe_file.py path\to\file.xlsx
```

To ignore entries from the same source, add `True` as the second argument

```PowerShell
python .\dedupe_file.py path\to\file.xlsx True
```

Yes, this needs to be done better.

## To-do

* Add tests (see: https://gist.github.com/sloria/7001839)
* Incorporate numba (see: https://stackoverflow.com/questions/35215161/most-efficient-way-to-map-function-over-numpy-array): compiled code should be a lot faster
* Set rows to automatically sort and format based off the score (see: https://stackoverflow.com/a/46313587). Rows should should also be shuffled before processing if ignore_same_source is `True`
* Set up a webserver
