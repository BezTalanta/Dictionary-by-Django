from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User
from .utilities import parse_translation


CATEGORY_CHOICE = (
    ("0", '0'),
    ("1", '1'),
    ("2", '2'),
    ("3", '3'),
)


class Word(models.Model):
    '''
        user *
        english
        transcription
        translation
        pure_translation *
        note
        favourite
        category
    '''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dictionary'
    )

    english = models.CharField(
        max_length=100,
        verbose_name='Английское слово',
    )

    transcription = models.CharField(
        max_length=100,
        verbose_name='Транскрипция',
        blank=True,
        null=True,
    )

    translation = models.CharField(
        max_length=200,
        verbose_name='Перевод'
    )

    pure_translation = models.CharField(
        'Чистый перевод',
        max_length=200,
        default=''
    )

    note = models.CharField(
        max_length=100,
        verbose_name='Заметка',
        blank=True,
        null=True,
    )

    favourite = models.BooleanField(
        default=False,
        verbose_name='Избранное ли слово'
    )

    category = models.CharField(
        max_length=5,
        choices=CATEGORY_CHOICE,
        default='0',
        verbose_name='Категория'
    )

    def __str__(self):
        return self.english

    def get_absolute_url(self):
        return reverse('detail-word', kwargs={'id': self.id})

    class Meta:
        db_table = 'word_table'
        managed = True
        verbose_name = 'Word'
        verbose_name_plural = 'Words'
        ordering = ('english',)
        unique_together = 'user', 'english'

    def set_original_translation(self, dirty_translation):
        '''
            Is using for get good translation with lower case format
            and then convert it to pure translation
        '''
        if len(dirty_translation) == 0:
            raise
        self.translation = dirty_translation.lower()
        l_dtrnslt = []
        for item in self.translation.split(','):
            item = item.strip()
            if item[0] == '+' or item[0] == '-':
                item = item[1:]
            l_dtrnslt.append(item)
        l_dtrnslt[0] = l_dtrnslt[0].title()
        self.pure_translation = ', '.join(l_dtrnslt)


class DictionarySetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    category = models.BooleanField(default=False)
    favourite = models.BooleanField(default=False)
    note = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user) + "'s setting"


class RunSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 50/50 - ff, only english word - w, only transcription - t
    show_type = models.CharField(max_length=20)
    is_endless = models.BooleanField(default=False)
    is_answer_menu = models.BooleanField(default=False)
    # '''
    #     This variable uses to prevent one ugly bug, if you refresh site
    #     you will send a lot of much get requests and at the one moment you
    #     can get word instead of transcription
    # '''
    # prevent_refresh = models.BooleanField(default=False)
    start_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return \
            f"{self.user}'s setting, created {self.start_time}, with show type: {self.show_type}, endless? {self.is_endless}, answer? {self.is_answer_menu}"


class RunWordManager(models.Manager):
    def get_first_active(self, user):
        return self.get_queryset().filter(user=user).filter(active_status=True).first()

    def get_user_words(self, user):
        return self.get_queryset().filter(user=user)


class RunWord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    active_status = models.BooleanField('Появилось ли слово', default=True)
    answer_status = models.BooleanField(
        'Статус правильности ответа', default=False)
    user_answer = models.CharField(
        'Ответ пользователя', max_length=200, default='')
    manager = RunWordManager()

    def check_translation(self, user_translation):
        right_translation_map = parse_translation(self.word.translation)
        user_translation_map = parse_translation(user_translation)
        zero_p, one_p, n_one_p = {}, {}, {}
        is_word_exists_with_zero, is_zero_priority_was = False, False
        is_result_right = True
        for word, priority in right_translation_map.items():
            if priority == 0:  # If priority 0 you can get only Wrong or one True
                is_word_exists_with_zero = True
                if user_translation_map.get(word, 'Not found') != 'Not found':
                    is_zero_priority_was = True
                    zero_p[word] = 1
                    del user_translation_map[word]
                else:
                    zero_p[word] = 0
            elif priority == 1:  # If priority 1 you can get only True or Wrong
                if user_translation_map.get(word, 'Not found') != 'Not found':
                    one_p[word] = 1  # Only True
                    del user_translation_map[word]
                else:
                    is_result_right = False
                    one_p[word] = -1  # Only Wrong
            else:  # If priority -1 you can get only True or nothing
                if user_translation_map.get(word, 'Not found') != 'Not found':
                    n_one_p[word] = 1
                    del user_translation_map[word]
                else:
                    n_one_p[word] = 0
        bad_user_input = [word for word in user_translation_map.keys()]
        result_right = (is_word_exists_with_zero ==
                        False or is_zero_priority_was) and is_result_right
        return {
            'is_zero_right': is_zero_priority_was,
            'zero_map': zero_p,
            'o_map': one_p,
            'n_o_map': n_one_p,
            'wrong_user_input': bad_user_input,
            'global_right': result_right,
        }

    def get_user_words(request):
        ''' Using to get all current user's words '''
        return RunWord.objects.filter(user=request.user)

    def __str__(self):
        return f"{self.user}'s word - {self.word}"
