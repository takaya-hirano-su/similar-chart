from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Currency)
admin.site.register(BidAsk)
admin.site.register(UserNetAsset)
admin.site.register(UserCoin)
admin.site.register(UserCurrnecy)