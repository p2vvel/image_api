from django.contrib import admin

# Register your models here.

from .models import Tier, User, UploadedImage, AvailableHeight
from django.urls import reverse
from django.utils.html import format_html


class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ["username", "view_tier"]

    @admin.display(empty_value="Basic", description="Tier")
    def view_tier(self, obj) -> bool:
        return obj.tier
        


class UploadedImageAdmin(admin.ModelAdmin):
    model = UploadedImage
    list_display = ["title", "view_owner", "height", "_original"]
    readonly_fields = ["image", "image_tag", "height", "parent", "owner", "title"]    # filled automatically
    list_filter = ["owner__username", ("parent", admin.EmptyFieldListFilter)]

    @admin.display(description="Owner")
    def view_owner(self, obj) -> str:
        url = reverse("admin:api_user_change", args=(obj.owner.pk,))
        return format_html(f"<a href='{url}'>{obj.owner}</a>")
            # obj.owner
    
    @admin.display(description="Original", boolean=True)
    def _original(self, obj):
        return obj.parent is None

    def image_tag(self, obj):
        """Get html img tag with image as src"""
        return format_html(f'<img alt="{obj.title}" src="{reverse("get_image", args=(obj.image.name, ))}" height="300px">')



class AvailableHeightAdmin(admin.ModelAdmin):
    model = AvailableHeight
    readonly_fields = ["height"]        # changing height in this model would be useless and make additional problems (generating new thumbnails)
    ordering = ["height"]



class TierAdmin(admin.ModelAdmin):
    model = Tier
    list_display = ["name", "original_image", "binary_image", "extra_image_sizes"]
    list_filter = ["original_image", "binary_image"]



admin.site.register(Tier, TierAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(UploadedImage, UploadedImageAdmin)
admin.site.register(AvailableHeight, AvailableHeightAdmin)