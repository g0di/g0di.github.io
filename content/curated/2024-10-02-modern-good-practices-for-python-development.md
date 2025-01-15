Title: Modern good practices for Python development
Tags: python, good-practices
Author: Stuart Ellis
Url: https://www.stuartellis.name/articles/python-modern-practices/
Save_As:

I should definitively write my own set of guidelines and practices for Python development. For the moment you can already find some in this article. I agree with most of the practices outlined expect maybe using TOML for configuration files (I prefer relying on environment variables and `.env` files). I would also recommend to opt for [typer](https://typer.tiangolo.com/) instead of `argparse` for more complex CLIs. Finally I would suggest using tools like [uv](https://github.com/astral-sh/uv) or [pdm](https://pdm-project.org) to manage your project (packaging, dependencies, virtual environment).
