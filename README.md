# requirement-files-unit-tests
This action provides unit test for Splunk TA's requirement logs.
test_lib contains tests for xml format checking, schema validating and cim model mapping.

steps:
Include following in the workflow file to run unit tests on the requirement logs in input_file directory
```
uses:  splunk/requirement-files-unit-tests@main
        with:
          input-files: tests/requirement_test/
```

For archiving test results in case of failure add following to workflow.yml
```
 - name: Archive production artifacts
        if: ${{ failure() }}
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: |
            test_*.txt
```
# License

The scripts and documentation in this project are released under the [LICENSE](LICENSE)

Copyright (C) 2021 Splunk Inc. All rights reserved.
