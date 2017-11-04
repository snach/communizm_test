from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO


class Test1(TestCase):
    def test_command_output(self):
        data_file = 'hi'
        out = StringIO()
        call_command('communizm', stdin=data_file, stdout=out)
        print out.getvalue()