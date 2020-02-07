import subprocess
import os
import psutil

from apollo.utils.console_utils import apollo_logo, OutputStyler, clear, stdout_print


class ConsoleManager:
    def __init__(self, log_settings):
        self.log_settings = log_settings
        # self.dynamic_energy_ratio = None
        # self.energy_threshold = None

    def console_output(self, text):
        clear()

        stdout_print(apollo_logo)

        stdout_print("  NOTE: CTRL + C If you want to Quit.")

        print(OutputStyler.HEADER + '-------------- INFO --------------' + OutputStyler.ENDC)

        print(OutputStyler.HEADER + 'SYSTEM ---------------------------' + OutputStyler.ENDC)
        print(OutputStyler.BOLD +
              'RAM USAGE: {0:.2f} GB'.format(self._get_memory()) + OutputStyler.ENDC)

        # print(OutputStyler.HEADER + 'MIC ------------------------------' + OutputStyler.ENDC)
        # print(OutputStyler.BOLD +
        #       'ENERGY THRESHOLD LEVEL: ' + '|' * int(self.energy_threshold) + '\n'
        #       'DYNAMIC ENERGY LEVEL: ' + '|' * int(self.dynamic_energy_ratio) + OutputStyler.ENDC)
        # print(' ')

        print(OutputStyler.HEADER + '-------------- LOG --------------' + OutputStyler.ENDC)
        lines = subprocess.check_output(['tail', '-10', self.log_settings['handlers']['file']['filename']]).decode("utf-8")
        print(OutputStyler.BOLD + lines + OutputStyler.ENDC)

        print(OutputStyler.HEADER + '-------------- ASSISTANT --------------' + OutputStyler.ENDC)
        print(OutputStyler.BOLD + '> ' + text + '\r' + OutputStyler.ENDC)

    @staticmethod
    def _get_memory():
        pid = os.getpid()
        py = psutil.Process(pid)
        return py.memory_info()[0] / 2. ** 30  # memory use in GB...I think