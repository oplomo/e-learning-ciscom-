# Generated by Django 5.0.6 on 2024-08-14 07:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_remove_result_score_result_module_scores_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='overall_performance',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.CreateModel(
            name='Perfomance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('date_recorded', models.DateField(auto_now_add=True)),
                ('enrollment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='courses.enrollment')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='courses.module')),
            ],
            options={
                'unique_together': {('enrollment', 'module')},
            },
        ),
        migrations.DeleteModel(
            name='Result',
        ),
    ]
