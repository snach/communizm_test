import json
import os
import signal
import sys
import time

from django.core.management import call_command
from django.test import TestCase

from coordinates_sender import send_packet


class Test1(TestCase):
    def test_command_output(self):

        hight = -267
        control_id = b'EyGeDCfJ'
        r, w = os.pipe()

        pid = os.fork()
        self.assertGreaterEqual(pid, 0)
        if pid > 0:
            os.close(w)
            r = os.fdopen(r, 'r', 0)
            time.sleep(2)
            send_packet(hight, control_id)
            os.kill(pid, signal.SIGTERM)

        elif pid == 0:
            os.close(r)
            StdOut = sys.stdout.fileno()
            sys.stdout = os.fdopen(StdOut, 'w', 0)
            os.dup2(w, StdOut)
            call_command('communizm', stdin="hi")

        result = r.read().split("\n")
        response_dict = json.loads(result[4].replace("\'", "\""))
        keys_in_response = ('event_type', 'control_id', 'lon', 'height', 'time', 'lat')

        for key in keys_in_response:
            self.assertTrue(response_dict.has_key(key))

        self.assertEqual(hight, response_dict.get("height"))
        self.assertEqual(control_id, response_dict.get("control_id"))
