import json
import locale
from pathlib import Path


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

    def get_translation(self, dot_notation_key: str, to_translate: str) -> str:
        keys = dot_notation_key.split('.')
        node = self.translations

        for key in keys:
            if node.get(key, None) is None:
                return to_translate
            node = node[key]

        return node[to_translate] if to_translate in node else node
