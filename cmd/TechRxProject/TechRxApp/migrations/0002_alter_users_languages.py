# Generated by Django 4.2 on 2023-05-05 12:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("TechRxApp", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="users",
            name="LANGUAGES",
            field=models.CharField(
                choices=[
                    ("English", "English"),
                    ("Hindi", "Hindi"),
                    ("Punjabi", "Punjabi"),
                    ("Telugu", "Telugu"),
                    ("Tamil", "Tamil"),
                    ("Kannada", "Kannada"),
                    ("Malayalam", "Malayalam"),
                    ("Marathi", "Marathi"),
                    ("French", "French"),
                    ("Japanese", "Japanese"),
                ],
                default="English",
                max_length=50,
            ),
        ),
    ]