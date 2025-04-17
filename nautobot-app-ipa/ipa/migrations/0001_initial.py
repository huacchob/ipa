# Generated by Django 4.2.20 on 2025-04-17 15:14

import django.core.serializers.json
from django.db import migrations, models
import nautobot.core.models.fields
import nautobot.extras.models.mixins
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('extras', '0122_add_graphqlquery_owner_content_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='IpaExampleModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('_custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('tags', nautobot.core.models.fields.TagsField(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(nautobot.extras.models.mixins.DynamicGroupMixin, nautobot.extras.models.mixins.NotesMixin, models.Model),
        ),
    ]
