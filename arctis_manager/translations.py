from dataclasses import dataclass, field
import json
import locale
import logging
from pathlib import Path
from typing import Optional


@dataclass
class TranslatableText:
    dot_notation_key: str
    format_dict: Optional[dict] = field(default_factory=lambda: {})

    def format(self, **kwargs):
        self.format_dict = kwargs or {}

        return self

    def __str__(self):
        if not hasattr(self, '_text'):
            self._text = Translations.get_instance().get_translation(self.dot_notation_key).format(**(self.format_dict or {}))

        return self._text

    def __hash__(self):
        return str(self).__hash__()


class Translations:
    translations: dict
    log: logging.Logger

    @staticmethod
    def get_instance(log_level: int = logging.INFO):
        if not hasattr(Translations, '_instance'):
            Translations._instance = Translations(log_level)
        return Translations._instance

    def __init__(self, log_level: int):
        self.log = logging.getLogger(__class__.__name__)
        self.log.setLevel(log_level)

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

        for sub_key in keys:
            if node.get(sub_key, None) is None:
                self._cache[key] = node
                self.log.warning(f'Missing translation for key: {key}')

                return self._cache[key]
            node = node[sub_key]

        self._cache[key] = node

        return self._cache[key]

    def debug_hit_cache(self):
        keys = list(self._cache.keys())
        keys.sort()

        self.log.debug(f'Hit keys:\n{'\n'.join(keys)}')
