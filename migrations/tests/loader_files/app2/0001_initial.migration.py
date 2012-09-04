from migrations.api import *


class Migration(BaseMigration):

    actions = [
        CreateModel(
            name = "Book",
            fields = [
                ("title", Field("django.db.models.fields.CharField", [], {"max_length": "100"})),
                ("author", Field("django.db.models.fields.related.ForeignKey", ["app1.Author"], {})),
            ],
        ),
    ]
