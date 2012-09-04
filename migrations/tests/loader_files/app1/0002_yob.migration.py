from migrations.api import *


class Migration(BaseMigration):

    dependencies = [
        ("app2", "0001_initial")
    ]

    actions = [
        CreateField(
            model_name = "Author",
            name = "yob",
            field = Field("django.db.models.fields.IntegerField", [], {}),
        ),
    ]
