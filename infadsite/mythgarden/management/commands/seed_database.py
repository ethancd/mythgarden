from django.core.management.base import BaseCommand, CommandError
import csv
import sys

# noinspection PyUnresolvedReferences
from mythgarden.models import *


def str_to_class(classname: str):
    try:
        return getattr(sys.modules[__name__], classname)
    except AttributeError:
        raise CommandError(f'Could not find class {classname}')


class Command(BaseCommand):
    help = 'Seeds the database with initial data read in from a csv file.'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='Path to csv file containing initial data')

    def handle(self, *args, **options):
        with open(options['path']) as f:
            reader = csv.reader(f)

            cls = None
            field_names = []
            expecting_header = True

            created_count = 0
            found_count = 0

            per_model_created_count = 0
            per_model_found_count = 0

            for row in reader:
                # sheet will be organized like this:
                # Model_A, field_1, field_2, field_3, ...
                # Model_A, value, value, value
                # Model_A, value, value, value
                # [blank row]
                # Model_B, field_1, field_2, field_3, ...
                # Model_B, value, value, value
                # etc.

                if options['verbosity'] == 3:
                    self.stdout.write(f'row {reader.line_num}: {row}')

                # so we'll take blank rows as the signal that the next row is a header for the next model
                if all(v == '' for v in row):
                    self.stdout.write(f'reading row {reader.line_num} as blank row')

                    if cls is not None:
                        self.stdout.write(f'Done with {cls.__name__} for now,'
                                          f'created {per_model_created_count} and found {per_model_found_count}')
                        per_model_created_count = 0
                        per_model_found_count = 0

                    expecting_header = True
                    continue

                # when we're expecting a header, we get the model with the first column,
                # then the field_names (to be used as the keys in constructing kwargs) as the rest of the columns
                # ... although strip out any blank columns
                if expecting_header:
                    self.stdout.write(f'reading row {reader.line_num} as header: classname {row[0]}, field_names {row[1:]}')
                    cls = str_to_class(row[0])
                    field_names = [v for v in row[1:] if v != '']
                    expecting_header = False
                    continue

                # otherwise, we're expecting data
                # let's ensure the model matches, why not right?
                if cls.__name__ != row[0]:
                    raise CommandError(f'Expected {cls.__name__} in row {reader.line_num} but got {row[0]}')

                # row values with any blank columns stripped out
                field_values = [v for v in row[1:] if v != '']

                # ensure field_names and row[1:] are the same length...
                if len(field_names) != len(field_values):
                    raise CommandError(f'Expected {len(field_names)} fields in row {reader.line_num} but got {len(field_values)}')

                # we zip the field names and the row values, then do a dict comprehension to get a dict of kwargs
                kwargs = {k: v for k, v in zip(field_names, field_values)}

                instance, created = cls.objects.get_or_create(**kwargs)

                if options['verbosity'] == 3:
                    self.stdout.write(f'row {reader.line_num}: {cls.__name__} with kwargs {kwargs}'
                                      f'gives {instance}, and created? {created}')

                if options['verbosity'] >= 2:
                    if created:
                        created_count += 1
                        per_model_created_count += 1
                        self.stdout.write(self.style.SUCCESS(f'Used {cls.__name__} with kwargs {kwargs} to create {instance}'))
                    else:
                        found_count += 1
                        per_model_found_count += 1
                        self.stdout.write(self.style.WARNING(f'Found {cls.__name__} with kwargs {kwargs}'))

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded database by creating {created_count} and finding {found_count} instances')
        )