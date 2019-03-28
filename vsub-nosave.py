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


def percentile(arr, percent):
    arr = sorted(arr)
    k = (len(arr) - 1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return arr[int(k)]
    d0 = arr[int(f)] * (c - k)
    d1 = arr[int(c)] * (k - f)
    return d0 + d1


def find_speech_regions(filename, frame_width=4096, min_region_size=0.5, max_region_size=6):
    reader = wave.open(filename)
    sample_width = reader.getsampwidth()
    rate = reader.getframerate()
    n_channels = reader.getnchannels()

    total_duration = reader.getnframes() / rate
    chunk_duration = float(frame_width) / rate

    n_chunks = int(total_duration / chunk_duration)
    energies = []

    for _c in range(n_chunks):
        chunk = reader.readframes(frame_width)
        energies.append(audioop.rms(chunk, sample_width * n_channels))

    threshold = percentile(energies, 0.2)

    elapsed_time = 0

    regions = []
    region_start = None

    # i = 1
    for energy in energies:
        is_silence = energy <= threshold
        max_exceeded = region_start and elapsed_time - region_start >= max_region_size

        if (max_exceeded or is_silence) and region_start:
            if elapsed_time - region_start >= min_region_size:
                # regions.append((i, region_start, elapsed_time))
                regions.append((region_start, elapsed_time))
                region_start = None
                # i += 1

        elif (not region_start) and (not is_silence):
            region_start = elapsed_time
        elapsed_time += chunk_duration
    # print(regions.__len__())
    return regions


class SpeechRecognizer(object):
    def __init__(self, language="en", rate=44100, retries=3, api_key=API_KEY):
        self.language = language
        self.rate = rate
        self.api_key = api_key
        self.retries = retries

    def __call__(self, data):
        try:
            for _r in range(self.retries):
                url = GOOGLE_SPEECH_API_URL.format(lang=self.language, key=self.api_key)
                headers = {"Content-Type": "audio/x-flac; rate=%d" % self.rate}

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


class FLACConverter(object):
    def __init__(self, source_path, include_before=0.25, include_after=0.25):
        self.source_path = source_path
        self.include_before = include_before
        self.include_after = include_after

    def __call__(self, region):
        try:
            start, end = region
            start = max(0, start - self.include_before)
            end += self.include_after
            temp = tempfile.NamedTemporaryFile(suffix='.flac', delete=False)
            ff = FFmpeg(
                inputs={self.source_path: None},
                outputs={temp.name: ["-y", "-ss", str(start), "-t", str(end - start), "-loglevel", "error"]}
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
    # parser.add_argument('-k', '--key', help="license", default="")
    args = parser.parse_args()

    if not args.source_path:
        print("Vui lòng nhập đường dẫn video/ audio.")
        return 1

    if args.stt_language not in LANGUAGE_CODES.keys():
        print("Không hỗ trợ nhận dạng ngôn ngữ này.")
        return 1

    # start = timeit.default_timer()
    audio_filename, audio_rate = extract_audio(args.source_path)
    regions = find_speech_regions(audio_filename)
    pool = multiprocessing.Pool(10)
    converter = FLACConverter(source_path=audio_filename)
    stt = SpeechRecognizer(language=args.stt_language, rate=audio_rate, api_key=API_KEY)

    transcripts = []

    if regions:
        widgets = ["Xử lý âm thanh: ", Percentage(), ' ', ETA()]
        pbar = ProgressBar(widgets=widgets, maxval=len(regions)).start()
        extracted_regions = []
        for i, extracted_region in enumerate(pool.imap(converter, regions)):
            extracted_regions.append(extracted_region)
            pbar.update(i)
        pbar.finish()

        widgets = ["Nhận dạng: ", Percentage(), ' ', ETA()]
        pbar = ProgressBar(widgets=widgets, maxval=len(regions)).start()
        for i, transcript in enumerate(pool.imap(stt, extracted_regions)):
            transcripts.append(transcript)
            pbar.update(i)
        pbar.finish()

    print("Tạo file phụ đề...")

    timed_subtitles = [(r, t) for r, t in zip(regions, transcripts) if t]

    formatted_subtitles = srt_formatter(timed_subtitles)
    des_transcript_file = args.output

    if not des_transcript_file:
        base = os.path.splitext(args.source_path)[0]
        des_transcript_file = "{base}.{format}".format(base=base, format="srt")

    with open(des_transcript_file, 'wb') as f:
        f.write(formatted_subtitles.encode("utf-8"))

    print(Path(des_transcript_file).absolute())
    os.remove(audio_filename)
    # stop = timeit.default_timer()
    # print("Took: {0}s!".format(int(stop - start)))

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
