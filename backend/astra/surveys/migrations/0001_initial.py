# Generated by Django 2.2.1 on 2019-06-26 23:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('number', models.IntegerField(blank=True, null=True)),
                ('md', models.DecimalField(decimal_places=2, max_digits=10)),
                ('inc', models.DecimalField(decimal_places=3, max_digits=10)),
                ('azi', models.DecimalField(decimal_places=3, max_digits=10)),
                ('tvd', models.DecimalField(decimal_places=3, max_digits=10)),
                ('north', models.DecimalField(decimal_places=3, max_digits=10)),
                ('east', models.DecimalField(decimal_places=3, max_digits=10)),
                ('vertical_section', models.DecimalField(decimal_places=3, max_digits=10)),
                ('dogleg', models.DecimalField(decimal_places=3, max_digits=10)),
                ('build_rate', models.DecimalField(decimal_places=3, max_digits=10)),
                ('turn_rate', models.DecimalField(decimal_places=3, max_digits=10)),
                ('calculated_tf', models.DecimalField(decimal_places=3, max_digits=10)),
                ('calculated_ang', models.DecimalField(decimal_places=3, max_digits=10)),
                ('clos_dist', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('clos_azi', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('mag_total', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('grav_total', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('dip', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('temp', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('zero_vs', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('step_out', models.DecimalField(decimal_places=2, max_digits=10)),
                ('my', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('active', models.NullBooleanField()),
                ('uid', models.CharField(blank=True, max_length=50, null=True)),
                ('rig_time', models.DateTimeField(blank=True, null=True)),
                ('edr_dls', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('edr_dispNs', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('edr_dispEw', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('job', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='job_surveys', to='jobs.Job')),
            ],
            options={
                'verbose_name_plural': 'Surveys',
            },
        ),
    ]
