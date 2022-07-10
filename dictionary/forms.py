from django import forms
from .models import Word


class WordForm(forms.ModelForm):
    class Meta:
        model = Word
        # fields = ['english', 'transcription', 'translation', 'note', 'category']
        exclude = ['user', 'pure_translation']
        labels = {
            'english': 'English word *',
            'transcription': 'Transcription',
            'translation': 'Translation *',
            'note': 'Note',
            'category': 'Category',
            'favourite': 'Is your word favourite'
        }

        help_texts = {
            'english': 'Write english word',
            'transcription': 'Write transcription',
            'translation': 'Write translation',
            'note': 'Write note if you want',
            'category': 'Choose category of your word',
            'favourite': 'Choose if your word is in favourite category',
        }

        error_messages = {
            'name': {
                'required': 'This field cannot be empty'
            },
            'translation': {
                'required': 'This field cannot be empty'
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['transcription'].required = True # Thats work

    def save(self, commit=True):
        self.instance.set_original_translation(self.instance.translation)
        return super().save(commit)
