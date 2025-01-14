from urllib.parse import urljoin


AUTHOR = 'Benoît Godard'
SITENAME = 'Yet Another Dev Blog'
SITEURL = "http://localhost:8000"

PATH = "content"

TIMEZONE = 'Europe/Paris'
THEME= './themes/notmyidea2'

DEFAULT_LANG = 'en'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

# Blogroll
LINKS = (
    
)

# Social widget
SOCIAL = (
    ("GitHub", "https://github.com/g0di"),
    ("LinkedIn", "https://www.linkedin.com/in/benoit-godard-0b40a7122"),
)

# Menus and customizations
DISPLAY_PAGES_ON_MENU = False
DISPLAY_CATEGORIES_ON_MENU = False
MENUITEMS = (
    ('Articles', '/category/articles.html'),
    ('Curated', '/category/curated.html'),
    ('Tags', '/tags.html'),
    ('About me', '/pages/about.html'),
)


JINJA_FILTERS = { "urljoin": urljoin }