AUTHOR = 'Benoît Godard'
SITENAME = 'Yet Another Dev Blog'
SITEURL = ""

PATH = "content"

TIMEZONE = 'Europe/Paris'
THEME= 'notmyidea'

DEFAULT_LANG = 'en'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

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
    ('Test', '/pages/test.html'),
)