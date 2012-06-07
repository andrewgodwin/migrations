from django.management import BaseCommand
from south2.parser import MigrationParser


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        p = MigrationParser(args[0])
        print p.actions
