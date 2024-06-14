import os
import django
from django.conf import settings
from django.db.models import Q
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
django.setup()
from webapp.chat.prompt import *
from webapp.models import *
from django.contrib.auth.models import User



r = RecentExp
print(r)