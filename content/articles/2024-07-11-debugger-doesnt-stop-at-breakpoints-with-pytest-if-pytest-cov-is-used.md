Title: Debugger doesn't stop at breakpoints with pytest if pytest-cov is used
Tags: programming, python, how-to guide, pytest, pytest-cov
Description: Troubleshoot Python debugger not working as expected and stopping at breakpoints when using pytest and pytest-cov when debugging tests.

Recently, while trying to debug some of my `pytest` tests using VSCode, I discovered that my breakpoints were completely ignored and the tests never stopped. After nearly breaking my keyboard in frustration, I stumbled upon [this GitHub issue](https://github.com/microsoft/vscode-python/issues/693).

In short, using the `pytest-cov` plugin does not play well with debuggers. This is explained [here](https://pytest-cov.readthedocs.io/en/latest/debuggers.html) in the `pytest-cov` documentation itself.

There are several options to overcome this limitation, detailed in the GitHub issue. Since I always set coverage settings directly in my `pyproject.toml` file, the best option for me was to add a dedicated VSCode launch configuration to disable coverage when using the debugger for running my tests.

Here’s the `launch.json` file I added to my repository’s `.vscode` directory:

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
      "env": { "PYTEST_ADDOPTS": "--no-cov" }
    }
  ]
}
```

And that's it! Whenever I debug a test from VSCode (e.g., by clicking on the `Debug Test` button for any pytest test), this launch configuration is picked up automatically and disables code coverage.

## Bonus

If you have multiple Python projects, you might prefer to set this launch configuration directly in your VSCode settings to avoid copy-pasting it into all your projects.

Add the following to your `settings.json`:

```json
{
  // Other settings...
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
        "env": { "PYTEST_ADDOPTS": "--no-cov" }
      }
    ],
    "compounds": []
  }
  // Other settings...
}
```

This should help ensure your breakpoints are hit when debugging pytest tests in VSCode, without the interference of code coverage tools.
