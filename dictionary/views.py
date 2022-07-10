import random

from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django import views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.db import connection

from .forms import WordForm
from .models import CATEGORY_CHOICE, RunSettings, RunWord, Word, DictionarySetting


ENGLISH_COLUMN = 5
TRANSCRIPTION_COLUMN = 2
TRANSLATION_COLUMN = 5


class WordListView(LoginRequiredMixin, views.View):
    def get(self, request):
        current_setting = DictionarySetting.objects.get(user=request.user)
        Words = Word.objects.filter(user=request.user)
        SearchDefault = ''
        if request.POST.get('SearchField', False) != False:
            SearchDefault = request.POST['SearchField']
            Words = Words.filter(english__icontains=SearchDefault)
        return render(request, 'dict/list.html',
                      {'words': Words,
                       'SearchDefault': SearchDefault,
                       'hf_english_col': ENGLISH_COLUMN -
                                         current_setting.category -
                                         current_setting.favourite,
                       'hf_tnscrp_col': TRANSCRIPTION_COLUMN,
                       'hf_trnslt_col': TRANSLATION_COLUMN - current_setting.note,
                       'hf_category': current_setting.category,
                       'hf_favor': current_setting.favourite,
                       'hf_note': current_setting.note})

    def post(self, request):
        current_setting = DictionarySetting.objects.get(user=request.user)
        if request.POST.get('add', False) == '':
            return redirect('add-word')
        elif request.POST.get('btn_categories', False) == '':
            current_setting.category = not current_setting.category
        elif request.POST.get('btn_favourites', False) == '':
            current_setting.favourite = not current_setting.favourite
        elif request.POST.get('btn_notes', False) == '':
            current_setting.note = not current_setting.note
        current_setting.save()
        return self.get(request)


class AddWordView(views.View):
    def get(self, request):
        return render(request, 'dict/add_page.html')

    def post(self, request):
        english = request.POST['english']
        trnslt = request.POST['translation']
        if len(english) == 0 or len(trnslt) == 0:
            return render(request, 'dict/add_page.html',
                          {'err': 'English word and translation cannot be empty!'})

        trnscrp = request.POST.get('transcription', '')
        category = request.POST['category']
        note = request.POST.get('note', '')
        isf = False
        if request.POST.get('is_favourite', False):
            isf = True
        try:
            w = Word(
                user=request.user,
                english=english,
                transcription=trnscrp,
                # translation=trnslt,
                note=note,
                category=CATEGORY_CHOICE[int(category)][1],
                favourite=isf,
            )
            w.set_original_translation(trnslt)
            w.save()
        except:
            return render(request, 'dict/add_page.html', \
                          {'err': f'Word {english} is already exist!'})
        if request.POST.get('multiple', False):
            return render(request, 'dict/add_page.html', {'multiple_check': 'Yeah'})
        return redirect('dict-list')


class DetailWordView(views.View):
    def get(self, request, id):
        print(request.GET)
        back_href = 'dict-list'
        if request.GET.get('back', False) != False:
            back_href = request.GET['back']
        return render(request, 'dict/detail_page.html', {
            'word': Word.objects.get(id=id),
            'back_href': back_href,
        })

    def post(self, request, id):
        if request.POST['Button'] == 'Update':
            w = Word.objects.get(id=id)
            w.english = request.POST['english']
            w.transcription = request.POST['transcription']
            w.translation = request.POST['translation']
            w.category = CATEGORY_CHOICE[int(request.POST['category'])][1]
            w.favourite = True if request.POST.get(
                'favourite', False) else False
            w.note = request.POST['note']
            try:
                w.save()
            except IntegrityError:
                return render(request, 'dict/detail_page.html', {
                    'word': Word.objects.get(id=id),
                    'err': f"{request.POST['english']} is already exists in your dictionary",
                })
        else:
            Word.objects.get(id=id).delete()
        return redirect(reverse('dict-list'))


class ModelRunView(LoginRequiredMixin, views.View):
    '''
        Run view is the view to get user possibility to learn english words
            First of all u can choose settings which you want
                Settings:
                    1) Percent of English word and transcription
                    2) Category
                    3) Favourite
                    4) Endless training
                    6) Result at the end(maybe conflict with 4 article)

        Session keys (user.name {}):
            1) options
            2) category
            3) favourite
            4) endless
            5) answer
    '''

    def get(self, request):
        get_user_settings = RunSettings.objects.filter(user=request.user)
        if get_user_settings:
            show_type = get_user_settings[0].show_type
            get_word = RunWord.manager.get_first_active(request.user)
            if not get_word:
                all_words = RunWord.manager.get_user_words(request.user)
                if get_user_settings[0].is_endless is False:
                    g_count, b_count = 0, 0
                    for item in all_words:
                        if item.answer_status is True:
                            g_count += 1
                        else:
                            b_count += 1
                    return render(request, 'dict/run_word_end_page.html', {
                        'good_words_count': g_count,
                        'wrong_words_count': b_count,
                        'all_words_count': g_count + b_count,
                        'data': all_words,
                    })
                else:
                    if all_words.count() == 0:
                        get_user_settings.delete()
                        return redirect(reverse('run'))
                    for word in all_words:
                        word.active_status = True
                        word.save()
                    return redirect(reverse('run'))
            if show_type == 'ff':
                show_type = 'w' if random.randint(0, 1) else 't'
            if show_type == 'w' or len(get_word.word.transcription) == 0:
                return render(request, 'dict/run_word_page.html', {
                    'output': get_word.word.english,
                }
                )
            else:
                return render(request, 'dict/run_word_page.html', {
                    'output': get_word.word.transcription,
                }
                )
        return render(request, 'dict/run_page.html')

    def post(self, request):
        if request.POST.get('calculate_button', False) != False:
            RunSettings.objects.create(
                user=request.user,
                show_type=request.POST['options'],
                is_endless=True if request.POST.get(
                    'Endless', False) else False,
                is_answer_menu=True if request.POST.get(
                    'Answer', False) else False
            )
            category = request.POST['Category']
            use_favourite = True if request.POST.get(
                'Favourite', False) else False
            data = Word.objects.filter(user=request.user)
            if category != 'all':
                if use_favourite:
                    data = data.filter(
                        Q(category=CATEGORY_CHOICE[int(category)][1]) | Q(favourite=True))
                else:
                    data = data.filter(
                        category=CATEGORY_CHOICE[int(category)][1])
            shuffle_list = [i for i in range(data.count())]
            random.shuffle(shuffle_list)
            for index in shuffle_list:
                RunWord.manager.create(
                    user=request.user,
                    word=data[index]
                )
        elif request.POST.get('button', False) != False and \
                request.POST['button'] == 'Check':
            rs = RunWord.manager.get_first_active(request.user)
            answer_map = rs.check_translation(request.POST['input'])
            rs.user_answer = request.POST['input']
            rs.active_status = False
            rs.answer_status = answer_map['global_right']
            rs.save()
            if not RunSettings.objects.filter(user=request.user)[0].is_answer_menu:
                return render(request, 'dict/run_word_result_page.html', {
                    'global_right': rs.answer_status,
                    'output': request.POST['output_remember'],
                    'input': request.POST['input'],
                    'word': rs.word,
                    **answer_map,
                })
        elif request.POST.get('button', False) != False and \
                request.POST['button'] == 'start new':
            RunWord.manager.get_user_words(request.user).delete()
            RunSettings.objects.filter(user=request.user).delete()
        elif request.POST.get('button', False) != False and \
                request.POST['button'] == 'end training':
            RunSettings.objects.filter(
                user=request.user).update(is_endless=False)
            for word in RunWord.manager.get_user_words(request.user):
                word.active_status = False
                word.save()
        elif request.POST.get('english_word', False) != False:
            word = RunWord.manager.get(
                Q(word__english=request.POST['english_word']), Q(user=request.user))
            return render(request, 'dict/run_word_result_page.html', {
                'global_right': word.answer_status,
                'output': word.word.english,
                'input': word.user_answer,
                'word': word.word,
                **word.check_translation(word.user_answer),
            })
        elif request.POST.get('go_to_detail', False) is not False:
            return redirect(reverse('detail-word',
                                    kwargs={
                                        'id': Word.objects.get(
                                            Q(english=
                                              request.POST['go_to_detail']) &
                                            Q(user=request.user)).pk
                                    }
                                    )
                            )
        return redirect(reverse('run'))


class TestForms(views.View):
    def get(self, request):
        return render(request, 'dict/test_form_page.html', {
            'form': WordForm(),
        })

    def post(self, request):
        f = WordForm(request.POST, initial={'user': request.user})
        return render(request, 'dict/test_form_page.html', {
            'form': f,
        })
