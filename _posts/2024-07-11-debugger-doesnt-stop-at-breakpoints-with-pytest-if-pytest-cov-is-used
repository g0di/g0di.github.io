---
layout: post
title: "Debugger doesn't stop at breakpoints with pytest if pytest-cov is used"
tags: python troubleshooting pytest
---
Quite recently, while trying to debug some of my `pyest` tests using VSCode I just discovered that my breakpoints were completly ignored and the tests were never stopped. Once I've successfuly broke my keyboard I stumbled upon [this github issue](https://github.com/microsoft/vscode-python/issues/693).

In short, use of `pytest-cov` plugin does not play well with debuggers. This is actually explained [here](https://pytest-cov.readthedocs.io/en/latest/debuggers.html) in the `pytest-cov` documentation itself...

There is several options you have to overcome this limitation which are detailed on the github issue. On my side, I'm always setting coverage settings directly into my `pyproject.toml` file so the best option for me was to simply add a dedicated VSCode launch configuration to disable coverage when using the debugger for running my test.

Basically, I've added the following `launch.json` file into my repository `.vscode` directory
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python Debugger: Current File",
      "type": "debugpy",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "purpose": ["debug-test"],
      "justMyCode": true,
      // Must disable code coverage when debug tests using pytest otherwise breakpoints are ignored
      "env": { "PYTEST_ADDOPTS": "--no-cov" }
    }
  ]
}
```

And that's it! Whenever I debug a test from VSCode (i.e: by clicking on the `Debug Test` button for any pytest test on vscode, this launch configuration is picked up automatically and disable code coverage.

## Bonus

If you're having multiple python projects you may prefer to set this launch configuration directly into your VSCode settings to avoid copy/pasting it on all your project.
```json
# settings.json
// REDACTED
    "launch": {
        "configurations": [
            {
                "name": "Python: Global Debug Tests",
                "type": "debugpy",
                "request": "launch",
                "program": "${file}",
                "purpose": ["debug-test"],
                "console": "integratedTerminal",
                "justMyCode": true,
                // Must disable code coverage when debug tests using pytest otherwise breakpoints are ignored
                "env": {"PYTEST_ADDOPTS": "--no-cov"}
            }
        ],
        "compounds": []
    },
// REDACTED
```

> At some point I'm wondering if this should not be handled automagically by VSCode itself considering the debugger is on their hands


