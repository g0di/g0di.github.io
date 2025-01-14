from urllib.parse import urljoin


AUTHOR = 'Benoît Godard'
DEFAULT_LANG = 'en'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU = False
JINJA_FILTERS = { "urljoin": urljoin }
LINKS = (('fastapi-problem-details', 'https://github.com/g0di/fastapi-problem-details'),)
MENUITEMS = (
    ('Articles', '/category/articles.html'),
    ('Curated', '/category/curated.html'),
    ('Tags', '/tags.html'),
    ('About me', '/pages/about.html'),
)
PATH = "content"
SEO_ARTICLES_LIMIT = 20
SEO_ENHANCER = True
SEO_PAGES_LIMIT = 20
SITENAME = 'Yet Another Dev Blog'
SITEURL = "http://localhost:8000"
THEME= './themes/notmyidea2'
TIMEZONE = 'Europe/Paris'
SOCIAL = (
    ("GitHub", "https://github.com/g0di"),
    ("LinkedIn", "https://www.linkedin.com/in/benoit-godard-0b40a7122"),

)