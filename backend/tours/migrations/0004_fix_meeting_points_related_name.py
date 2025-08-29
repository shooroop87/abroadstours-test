# backend/tours/migrations/0004_fix_meeting_points_related_name.py
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('tours', '0003_tour_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tourmeetingpoint',
            name='tour',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='meeting_points',  # ИСПРАВЛЯЕМ: было tour_meeting_points
                to='tours.tour',
            ),
        ),
    ]