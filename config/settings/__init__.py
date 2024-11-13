import os

environment = os.getenv("DJANGO_ENV", "development")

if environment == "production":
    from .production import *  # noqa: F401, F403
elif environment == "testing":
    from .testing import *  # noqa: F401, F403
else:
    from .development import *  # noqa: F401, F403
