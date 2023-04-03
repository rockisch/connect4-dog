# Instructions

## Requirements

Python >= 3.10 is required.

## Running

To run this project, you'll need a virtual env. In the root directory, open your terminal and type:

```bash
# If your system has both Python 2 and Python 3 installed, use the `python3` command instead.
python -m venv env

# On Linux/MacOS
. env/bin/activate
# On Windows CMD
.\env\Scripts\Activate
# On Windows Powershell (may require some additional steps)
.\env\Scripts\Activate.ps1

pip install -r requirements.txt
```

Every time you open a new shell, you'll need to run the `activate`/`Activate`/`Activate.ps1` command again.

After setting up your virtual env, type this to start the project:

```bash
python connect4.py
```
