from django.contrib import admin
from filmApp.models import Profile, Film, Comment, Appraisal


class ProfileAdmin(admin.ModelAdmin):
    pass


class FilmAdmin(admin.ModelAdmin):
    pass


class CommentAdmin(admin.ModelAdmin):
    pass


class AppraisalAdmin(admin.ModelAdmin):
    pass

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Film, FilmAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Appraisal, AppraisalAdmin)