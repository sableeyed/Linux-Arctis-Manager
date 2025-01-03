import json
import locale
from pathlib import Path
from typing import Optional


class Translations:
    translations: dict

    @staticmethod
    def get_instance():
        if not hasattr(Translations, '_instance'):
            Translations._instance = Translations()
        return Translations._instance

    def __init__(self):
        lang_code, _ = locale.getdefaultlocale()
        lang_code = lang_code.split('_')[0]

        translation_json_path = Path(__file__).parent.joinpath('lang', f'{lang_code}.json')
        if not translation_json_path.is_file():
            translation_json_path = Path(__file__).parent.joinpath('lang', 'en.json')

        self.translations = json.load(translation_json_path.open('r'))

        self._cache = {}

    def get_translation(self, dot_notation_key: str, *additional_key_parts: list[str]) -> str:
        key = '.'.join([key for key in [dot_notation_key, *additional_key_parts] if key is not None])
        if key in self._cache:
            return self._cache[key]

        keys = key.split('.')
        node = self.translations

        for key in keys:
            if node.get(key, None) is None:
                self._cache[key] = node

                return key
            node = node[key]

        self._cache[key] = node

        return self._cache[key]
