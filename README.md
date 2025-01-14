# G0di personal blog

This is the source code of my personal software engineering blog. It is hosted on github pages and use Python [Pelican] library to generate the blog as a static site

## Installation

- Python >= 3.12 is required
- [PDM] is required

Git clone the project then

```bash
pdm install
pdm start
```

> This will build the static site and serve it locally on http://localhost:8000

## Configuration

Site generation configuration is defined in [pelicanconf.py](./pelicanconf.py).
Configuration of the site actually published on github pages is defined in [publishconf.py](./publishconf.py)

> The publish configuration extends the base configuration

## SEO

The generated website is automatically optimized for SEO. On build, a report is generated on project root: [seo_report.html](./seo_report.html).
This report provide guidance to further enhance SEO for articles and pages of the site.

[Pelican]: https://getpelican.com
[PDM]: https://pdm-project.org/en/latest/
