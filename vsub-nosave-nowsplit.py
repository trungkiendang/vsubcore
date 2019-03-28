# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import argparse
import audioop
import json
import math
import multiprocessing
import os
import sys
import tempfile
import wave
from pathlib import Path

import pysrt
import requests
import six
from ffmpy import FFmpeg
from progressbar import ProgressBar, Percentage, ETA

from constants import natural_keys

API_KEY = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
# "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
GOOGLE_SPEECH_API_URL = "http://www.google.com/speech-api/v2/recognize?client=chromium&lang={lang}&key={key}"
# RESULT_AUDIO = "Audios"

LANGUAGE_CODES = {
    'af': 'Afrikaans',
    'ar': 'Arabic',
    'az': 'Azerbaijani',
    'be': 'Belarusian',
    'bg': 'Bulgarian',
    'bn': 'Bengali',
    'bs': 'Bosnian',
    'ca': 'Catalan',
    'ceb': 'Cebuano',
    'cs': 'Czech',
    'cy': 'Welsh',
    'da': 'Danish',
    'de': 'German',
    'el': 'Greek',
    'en': 'English',
    'eo': 'Esperanto',
    'es': 'Spanish',
    'et': 'Estonian',
    'eu': 'Basque',
    'fa': 'Persian',
    'fi': 'Finnish',
    'fr': 'French',
    'ga': 'Irish',
    'gl': 'Galician',
    'gu': 'Gujarati',
    'ha': 'Hausa',
    'hi': 'Hindi',
    'hmn': 'Hmong',
    'hr': 'Croatian',
    'ht': 'Haitian Creole',
    'hu': 'Hungarian',
    'hy': 'Armenian',
    'id': 'Indonesian',
    'ig': 'Igbo',
    'is': 'Icelandic',
    'it': 'Italian',
    'iw': 'Hebrew',
    'ja': 'Japanese',
    'jw': 'Javanese',
    'ka': 'Georgian',
    'kk': 'Kazakh',
    'km': 'Khmer',
    'kn': 'Kannada',
    'ko': 'Korean',
    'la': 'Latin',
    'lo': 'Lao',
    'lt': 'Lithuanian',
    'lv': 'Latvian',
    'mg': 'Malagasy',
    'mi': 'Maori',
    'mk': 'Macedonian',
    'ml': 'Malayalam',
    'mn': 'Mongolian',
    'mr': 'Marathi',
    'ms': 'Malay',
    'mt': 'Maltese',
    'my': 'Myanmar (Burmese)',
    'ne': 'Nepali',
    'nl': 'Dutch',
    'no': 'Norwegian',
    'ny': 'Chichewa',
    'pa': 'Punjabi',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'ro': 'Romanian',
    'ru': 'Russian',
    'si': 'Sinhala',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'so': 'Somali',
    'sq': 'Albanian',
    'sr': 'Serbian',
    'st': 'Sesotho',
    'su': 'Sudanese',
    'sv': 'Swedish',
    'sw': 'Swahili',
    'ta': 'Tamil',
    'te': 'Telugu',
    'tg': 'Tajik',
    'th': 'Thai',
    'tl': 'Filipino',
    'tr': 'Turkish',
    'uk': 'Ukrainian',
    'ur': 'Urdu',
    'uz': 'Uzbek',
    'vi': 'Vietnamese',
    'yi': 'Yiddish',
    'yo': 'Yoruba',
    'zh-CN': 'Chinese (Simplified)',
    'zh-TW': 'Chinese (Traditional)',
    'zu': 'Zulu',
}


def reg(lang, data, rate=44100, retries=3, api_key=API_KEY):
    url = GOOGLE_SPEECH_API_URL.format(lang=lang, key=api_key)
    headers = {"Content-Type": "audio/x-flac; rate=%d" % rate}
    try:
        for _r in range(retries):
            try:
                resp = requests.post(url, data=data, headers=headers)
            except requests.exceptions.ConnectionError:
                continue

            for line in resp.content.decode('utf-8').split("\n"):
                try:
                    line = json.loads(line)
                    line = line['result'][0]['alternative'][0]['transcript']
                    xxx = line[:1].upper() + line[1:]
                    return xxx
                except:
                    continue
    except ValueError:
        return


def extract_audio(filename, channels=1, rate=16000):
    # temp = Path(filename).stem + ".wav"
    temp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    if not os.path.isfile(filename):
        print("Tệp tin không tồn tại: {0}".format(filename))
        raise Exception("Sai đường dẫn: {0}".format(filename))
    ff = FFmpeg(
        inputs={filename: None},
        outputs={temp.name: ["-y", "-ac", str(channels), "-ar", str(rate), "-loglevel", "error"]}
    )
    ff.run()
    return temp.name, rate


def flacConvert(source_path):
    try:
        temp = tempfile.NamedTemporaryFile(suffix='.flac', delete=False)
        ff = FFmpeg(
            inputs={source_path: None},
            outputs={temp.name: ["-y", "-loglevel", "error"]}
        )
        ff.run()
        return temp.read()

    except ValueError as err:
        print(err)
        return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source_path', help="Đường dẫn tới file video/audio", nargs='?')
    parser.add_argument('-o', '--output',
                        help="Thư mục lưu file phụ đề (mặc định lưu tại thư mục chứa file thực thi)")
    parser.add_argument('-S', '--stt-language', help="Ngôn ngữ nhận dạng", default="en")
    args = parser.parse_args()

    if not args.source_path:
        print("Vui lòng nhập đường dẫn video/ audio.")
        return 1

    if args.stt_language not in LANGUAGE_CODES.keys():
        print("Không hỗ trợ nhận dạng ngôn ngữ này.")
        return 1

    # start = timeit.default_timer()
    audio_filename, audio_rate = extract_audio(args.source_path)
    converter = flacConvert(source_path=audio_filename)
    stt = reg(args.stt_language, converter, rate=audio_rate)
    print(stt)
    des_file = args.output
    if not des_file:
        base, ext = os.path.splitext(args.source_path)
        des_file = "{base}.{format}".format(base=base, format="txt")
    print(des_file)
    with open(des_file, 'wb') as f:
        f.write(stt.encode("utf-8"))

    os.remove(audio_filename)

    return 0


def srt_formatter(subtitles, padding_before=0, padding_after=0):
    sub_rip_file = pysrt.SubRipFile()
    for i, ((start, end), text) in enumerate(subtitles, start=1):
        item = pysrt.SubRipItem()
        item.index = i
        item.text = six.text_type(text)
        item.start.seconds = max(0, start - padding_before)
        item.end.seconds = end + padding_after
        sub_rip_file.append(item)
    return '\n'.join(six.text_type(item) for item in sub_rip_file)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    sys.exit(main())
