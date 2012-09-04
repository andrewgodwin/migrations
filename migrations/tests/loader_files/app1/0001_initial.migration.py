from migrations.api import *


class Migration(BaseMigration):

    actions = [
        CreateModel(
            name = "Author",
            fields = [
                ("name", Field("django.db.models.fields.CharField", [], {"max_length": "100"})),
            ],
        ),
    ]
