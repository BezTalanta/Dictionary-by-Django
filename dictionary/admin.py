from django.contrib import admin
from .models import Word, RunWord, RunSettings, DictionarySetting

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    # list_display = ['__all__']
    search_fields = ('english', )
    ordering = ('english', )

admin.site.register(RunWord)
admin.site.register(RunSettings)
admin.site.register(DictionarySetting)