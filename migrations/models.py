from django.db import models


class AppliedMigration(models.Model):
    """
    Tracks a migration having been applied to this database.
    """

    app_label = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField(blank=True)

    def __unicode__(self):
        return "<%s: %s>" % (self.app_name, self.migration)
