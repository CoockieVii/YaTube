from django.contrib import admin

from posts.models import Post, Group, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'created', 'author', 'group',)
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'description',)
    list_filter = ('slug',)
    search_fields = ('slug',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    list_filter = ('user',)
    search_fields = ('user',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Follow, FollowAdmin)
