from urllib.parse import urljoin

AUTHOR = "Benoît Godard"
DEFAULT_LANG = "en"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU = False
JINJA_FILTERS = {"urljoin": urljoin}
LINKS = (
    ("fastapi-problem-details", "https://github.com/g0di/fastapi-problem-details"),
    ("rename", "https://github.com/g0di/rename"),
    ("media-helper", "https://github.com/g0di/media-helper"),
)
LINKS_WIDGET_NAME = "Projects"
LOGO = "https://g0di.github.io/images/benoit-godard.jpg"
MENUITEMS = (
    ("Articles", "/category/articles.html"),
    ("Curated", "/category/curated.html"),
    ("Categories", "/tags.html"),
    ("About me", "/pages/about.html"),
)
PATH = "content"
SEO_ARTICLES_LIMIT = 20
SEO_ENHANCER = True
SEO_ENHANCER_OPEN_GRAPH = True
SEO_ENHANCER_TWITTER_CARDS = True
SEO_PAGES_LIMIT = 20
SITENAME = "Yet Another Dev Blog"
SITEURL = "http://localhost:8000"
STATIC_PATHS = [
    "images",
    "favicon.ico",
    "apple-touch-icon.png",
    "favicon-16x16.png",
    "favicon-32x32.png",
    "site.webmanifest",
    "android-chrome-192x192.png",
    "android-chrome-512x512.png",
]
SUMMARY_MAX_LENGTH = None
SUMMARY_MAX_PARAGRAPHS = 1
THEME = "./themes/notmyidea2"
TIMEZONE = "Europe/Paris"
SOCIAL = (
    ("GitHub", "https://github.com/g0di"),
    ("LinkedIn", "https://www.linkedin.com/in/benoit-godard-0b40a7122"),
)
