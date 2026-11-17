from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "kilnworks-public-development-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]
ROOT_URLCONF = "foundry.urls"
MIDDLEWARE = ["django.middleware.common.CommonMiddleware", "django.middleware.csrf.CsrfViewMiddleware"]
INSTALLED_APPS = ["django.contrib.staticfiles", "core"]
TEMPLATES = [{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[BASE_DIR / "templates"],"APP_DIRS":True,"OPTIONS":{"context_processors":[]}}]
STATIC_URL = "/assets/"
STATIC_ROOT = BASE_DIR / "collected"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
