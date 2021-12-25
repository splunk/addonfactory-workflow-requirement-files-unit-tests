# addonfactory-workflow-requirement-files-unit-tests

This action provides unit test for Splunk TA's requirement logs.
`test_lib` contains tests for XML format checking, schema validating and CIM model mapping.

This action is intended for Splunk internal use.

## Running locally

Steps:

- `git clone git@github.com:splunk/addonfactory-workflow-requirement-files-unit-tests.git`
- `cd addonfactory-workflow-requirement-files-unit-tests`
- `python3 -m venv .venv`
- `source .venv/bin/activate`
- `pip install lxml==4.6.3`
- `python run_all.py --input <path-to-your-requiremenet-files>`

# License

The scripts and documentation in this project are released under the [Apache 2.0 License](LICENSE).
