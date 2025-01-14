# Generated by Django 5.0.6 on 2024-08-10 09:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_course_performance_module_performance_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='performance',
        ),
        migrations.RemoveField(
            model_name='module',
            name='performance',
        ),
        migrations.CreateModel(
            name='Performance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('main_exam_score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('overall_score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performances', to='courses.course')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performances', to='courses.module')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performances', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('student', 'module', 'course')},
            },
        ),
    ]
