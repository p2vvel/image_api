from django.contrib import admin

# Register your models here.

from .models import Tier, User, UploadedImage, AvailableHeight




class UserAdmin(admin.ModelAdmin):
    model = User


class UploadedImageAdmin(admin.ModelAdmin):
    model = UploadedImage


class AvailableHeightAdmin(admin.ModelAdmin):
    model = AvailableHeight


class TierAdmin(admin.ModelAdmin):
    model = Tier
    inlines = [AvailableHeight]


admin.site.register(Tier)
admin.site.register(User)
admin.site.register(UploadedImage)
admin.site.register(AvailableHeight)