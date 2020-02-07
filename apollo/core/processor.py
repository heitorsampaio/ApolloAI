import speech_recognition as sr
import time

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from apollo.core.controller import SkillController
from apollo.utils.startup_utils import start_up
from apollo.settings import GENERAL_SETTINGS, ANALYZER, ROOT_LOG_CONF
from apollo.skills.skills_registry import CONTROL_SKILLS, SKILLS
from apollo.skills.skill_analyzer import SkillAnalyzer
from apollo.settings import SPEECH_RECOGNITION
from apollo.engines.stt import STTEngine
from apollo.engines.tts import TTSEngine
from apollo.engines.ttt import TTTEngine
from apollo.core.nlp_processor import ResponseCreator
from apollo.core.console_manager import ConsoleManager


class Processor:
    def __init__(self):
        self.input_engine = STTEngine(
                                        pause_threshold=SPEECH_RECOGNITION['pause_threshold'],
                                        energy_theshold=SPEECH_RECOGNITION['energy_threshold'],
                                        ambient_duration=SPEECH_RECOGNITION['ambient_duration'],
                                        dynamic_energy_threshold=SPEECH_RECOGNITION['dynamic_energy_threshold'],
                                        sr=sr
                                        ) if GENERAL_SETTINGS['user_voice_input'] else TTTEngine()

        self.console_manager = ConsoleManager(
                                              log_settings=ROOT_LOG_CONF,
                                             )
        self.output_engine = TTSEngine(
                                        console_manager=self.console_manager,
                                        speech_response_enabled=GENERAL_SETTINGS['response_in_speech']
                                       )
        self.response_creator = ResponseCreator()

        self.skill_analyzer = SkillAnalyzer(
                                            weight_measure=TfidfVectorizer,
                                            similarity_measure=cosine_similarity,
                                            args=ANALYZER['args'],
                                            skills_=SKILLS,
                                            sensitivity=ANALYZER['sensitivity']
                                            )

        self.skill_controller = SkillController(
                                                settings_=GENERAL_SETTINGS,
                                                input_engine=self.input_engine,
                                                analyzer=self.skill_analyzer,
                                                control_skills=CONTROL_SKILLS,
                                                )

    def run(self):
        start_up()
        while True:
            self.skill_controller.wake_up_check()
            if self.skill_controller.is_assistant_enabled:  # Check if the assistant is waked up
                self._process()

    def _process(self):
            self.skill_controller.get_transcript()
            self.skill_controller.get_skills()
            if self.skill_controller.to_execute:
                response = self.response_creator.create_positive_response(self.skill_controller.latest_voice_transcript)
            else:
                response = self.response_creator.create_negative_response(self.skill_controller.latest_voice_transcript)

            self.output_engine.assistant_response(response)
            self.skill_controller.execute()