# Generated by Django 4.0.4 on 2022-05-14 20:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dictionary', '0002_alter_word_english_alter_word_note'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='word',
            options={'managed': True, 'ordering': ('-english',), 'verbose_name': 'Word', 'verbose_name_plural': 'Words'},
        ),
        migrations.AlterField(
            model_name='word',
            name='category',
            field=models.CharField(choices=[('0', '0'), ('1', '1'), ('2', '2'), ('3', '3')], default='0', max_length=5, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='word',
            name='translation',
            field=models.CharField(max_length=200, verbose_name='Перевод'),
        ),
        migrations.CreateModel(
            name='DictionarySetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.BooleanField(default=False)),
                ('favourite', models.BooleanField(default=False)),
                ('note', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
