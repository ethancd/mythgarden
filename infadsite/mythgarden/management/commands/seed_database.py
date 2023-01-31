from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
import sys
import csv
import re

# noinspection PyUnresolvedReferences
from mythgarden.models import *
from ._command_helpers import str_to_class, snakecase_to_titlecase

SKIP_VALUES = ['default', 'none', 'null', 'skip']


def parse_fk_cell(field_name, field_value):
    """
    1. get the class name of ref'd model from field_name (e.g. fk__place__surround -> Place)
    2. get the ref'd instance using natural key lookup of field_value
    3. get the cleaned field name (e.g. fk__place__surround -> surround)
    4. return the cleaned field name as the key and the instance as the value

    throw errors if the class or instance don't exist,
    or if the field_name doesn't conform to expected format
    """

    if re.fullmatch(r'fk__\w+__\w+', field_name) is None:
        raise CommandError(f'Field name {field_name} does not conform to expected format: fk__\\w+__\\w+')

    foreign_classname_snakecase, cleaned_field_name = re.match(r'^fk__(\w+)__(\w+)', field_name).group(1, 2)
    foreign_classname = snakecase_to_titlecase(foreign_classname_snakecase)
    foreign_cls = str_to_class(sys.modules[__name__], foreign_classname)

    foreign_instance = foreign_cls.objects.get_by_natural_key(field_value)
    if foreign_instance is None:
        raise CommandError(f'Could not find instance of {foreign_classname} with natural key {field_value}')

    return cleaned_field_name, foreign_instance


class Command(BaseCommand):
    help = 'Seeds the database with initial data read in from a csv file.'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='Path to csv file containing initial data')
        parser.add_argument('--flush-table', type=str, nargs='*', help='Flush the specified table(s) before seeding')

    def handle(self, *args, **options):
        if options['flush_table']:
            try:
                call_command('flush_table', table=options['flush_table'])
            except CommandError as e:
                self.stdout.write(self.style.ERROR(f'Could not flush table(s): {e}. Halting execution.'))
                return

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
                        self.stdout.write(self.style.SUCCESS(f'{cls.__name__} complete: '
                                          f'created {per_model_created_count} and found {per_model_found_count}'))
                        per_model_created_count = 0
                        per_model_found_count = 0
                        cls = None

                    expecting_header = True
                    continue

                # when we're expecting a header, we get the model with the first column,
                # then the field_names (to be used as the keys in constructing kwargs) as the rest of the columns
                # ... although strip out any blank columns
                if expecting_header:
                    self.stdout.write(f'reading row {reader.line_num} as header: classname {row[0]}, field_names {row[1:]}')
                    cls = str_to_class(sys.modules[__name__], row[0])
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

                # if any field name starts with fk__, e.g. fk__place__surround:
                # the current field_value is the natural key of the referenced class, and
                # we need to get the cleaned field name (e.g. surround) and the instance of the referenced model

                cleaned_field_names = field_names.copy()

                for i, field_name in enumerate(field_names):
                    if field_name.startswith('fk__') and field_values[i] not in SKIP_VALUES:
                        cleaned_field_name, foreign_instance = parse_fk_cell(field_name, field_values[i])

                        cleaned_field_names[i] = cleaned_field_name
                        field_values[i] = foreign_instance

                # we zip the field names & values into a dict of kwargs,
                # but we'll skip any fields that have the value 'default', 'none', (or any other value in SKIP_VALUES)
                kwargs = {k: v for k, v in zip(cleaned_field_names, field_values) if v not in SKIP_VALUES}

                instance, created = cls.objects.get_or_create(**kwargs)

                if options['verbosity'] == 3:
                    self.stdout.write(f'row {reader.line_num}: {cls.__name__} with kwargs {kwargs}'
                                      f'gives {instance}, and created? {created}')

                if created:
                    created_count += 1
                    per_model_created_count += 1
                    if options['verbosity'] >= 2:
                        self.stdout.write(self.style.SUCCESS(f'Used {cls.__name__} with kwargs {kwargs} to create {instance}'))
                else:
                    found_count += 1
                    per_model_found_count += 1
                    if options['verbosity'] >= 2:
                        self.stdout.write(self.style.WARNING(f'Found {cls.__name__} with kwargs {kwargs}'))

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded database by creating {created_count} and finding {found_count} instances')
        )