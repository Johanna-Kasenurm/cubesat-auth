### Create a virtual environment:
```python -m venv .venv```
### Activate the virtual environment:
Bash: ```source .venv/Scripts/activate```
Powershell: ```.\.venv\Scripts\Activate.ps1```
### Install the project dependencies:
```pip install -r requirements.txt```
### Deactivate the virtual environment:
```deactivate```
### Run all tests
```pytest -v```
### Run one test file
```pytest tests/test_auth.py -v```
### Run one test
```pytest tests/test_auth.py::test_init_and_login_success -v```

