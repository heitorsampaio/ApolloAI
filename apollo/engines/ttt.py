import logging


class TTTEngine:
    """
    Text To Text Engine (TTT)
    """
    def __init__(self):
        self.logger = logging

    def recognize_input(self):
        self.logger.info("Waiting for user input.")
        voice_transcript = input('>> ').lower()
        while voice_transcript == '':
            self.logger.info("User didn't said something")
            voice_transcript = input('>> ').lower()
        return voice_transcript