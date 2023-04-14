from django.contrib import admin
from .models import *

admin.site.register(Market)
admin.site.register(Pair)
admin.site.register(OHLC)