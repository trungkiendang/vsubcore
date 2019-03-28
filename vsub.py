import jsonimport mathimport multiprocessingimport osimport requestsimport waveimport argparseimport audioopfrom pathlib import Pathfrom ffmpy import FFmpegfrom formatters import FORMATTERSimport sysimport timeitfrom constants import natural_keysfrom progressbar import ProgressBar, Percentage, ETAGOOGLE_SPEECH_API_KEY = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"# "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"GOOGLE_SPEECH_API_URL = "http://www.google.com/speech-api/v2/recognize?client=chromium&lang={lang}&key={key}"RESULT_AUDIO = "Audios"LANGUAGE_CODES = {    'af': 'Afrikaans',    'ar': 'Arabic',    'az': 'Azerbaijani',    'be': 'Belarusian',    'bg': 'Bulgarian',    'bn': 'Bengali',    'bs': 'Bosnian',    'ca': 'Catalan',    'ceb': 'Cebuano',    'cs': 'Czech',    'cy': 'Welsh',    'da': 'Danish',    'de': 'German',    'el': 'Greek',    'en': 'English',    'eo': 'Esperanto',    'es': 'Spanish',    'et': 'Estonian',    'eu': 'Basque',    'fa': 'Persian',    'fi': 'Finnish',    'fr': 'French',    'ga': 'Irish',    'gl': 'Galician',    'gu': 'Gujarati',    'ha': 'Hausa',    'hi': 'Hindi',    'hmn': 'Hmong',    'hr': 'Croatian',    'ht': 'Haitian Creole',    'hu': 'Hungarian',    'hy': 'Armenian',    'id': 'Indonesian',    'ig': 'Igbo',    'is': 'Icelandic',    'it': 'Italian',    'iw': 'Hebrew',    'ja': 'Japanese',    'jw': 'Javanese',    'ka': 'Georgian',    'kk': 'Kazakh',    'km': 'Khmer',    'kn': 'Kannada',    'ko': 'Korean',    'la': 'Latin',    'lo': 'Lao',    'lt': 'Lithuanian',    'lv': 'Latvian',    'mg': 'Malagasy',    'mi': 'Maori',    'mk': 'Macedonian',    'ml': 'Malayalam',    'mn': 'Mongolian',    'mr': 'Marathi',    'ms': 'Malay',    'mt': 'Maltese',    'my': 'Myanmar (Burmese)',    'ne': 'Nepali',    'nl': 'Dutch',    'no': 'Norwegian',    'ny': 'Chichewa',    'pa': 'Punjabi',    'pl': 'Polish',    'pt': 'Portuguese',    'ro': 'Romanian',    'ru': 'Russian',    'si': 'Sinhala',    'sk': 'Slovak',    'sl': 'Slovenian',    'so': 'Somali',    'sq': 'Albanian',    'sr': 'Serbian',    'st': 'Sesotho',    'su': 'Sudanese',    'sv': 'Swedish',    'sw': 'Swahili',    'ta': 'Tamil',    'te': 'Telugu',    'tg': 'Tajik',    'th': 'Thai',    'tl': 'Filipino',    'tr': 'Turkish',    'uk': 'Ukrainian',    'ur': 'Urdu',    'uz': 'Uzbek',    'vi': 'Vietnamese',    'yi': 'Yiddish',    'yo': 'Yoruba',    'zh-CN': 'Chinese (Simplified)',    'zh-TW': 'Chinese (Traditional)',    'zu': 'Zulu',}def percentile(arr, percent):    arr = sorted(arr)    k = (len(arr) - 1) * percent    f = math.floor(k)    c = math.ceil(k)    if f == c:        return arr[int(k)]    d0 = arr[int(f)] * (c - k)    d1 = arr[int(c)] * (k - f)    return d0 + d1def find_speech_regions(filename, frame_width=4096, min_region_size=0.5, max_region_size=6):    reader = wave.open(filename)    sample_width = reader.getsampwidth()    rate = reader.getframerate()    n_channels = reader.getnchannels()    total_duration = reader.getnframes() / rate    chunk_duration = float(frame_width) / rate    n_chunks = int(total_duration / chunk_duration)    energies = []    for _c in range(n_chunks):        chunk = reader.readframes(frame_width)        energies.append(audioop.rms(chunk, sample_width * n_channels))    threshold = percentile(energies, 0.2)    elapsed_time = 0    regions = []    region_start = None    i = 1    for energy in energies:        is_silence = energy <= threshold        max_exceeded = region_start and elapsed_time - region_start >= max_region_size        if (max_exceeded or is_silence) and region_start:            if elapsed_time - region_start >= min_region_size:                regions.append((i, region_start, elapsed_time))                region_start = None                i += 1        elif (not region_start) and (not is_silence):            region_start = elapsed_time        elapsed_time += chunk_duration    print(regions.__len__())    return regionsclass SpeechRecognizer(object):    def __init__(self, language="en", rate=44100, retries=3, api_key=GOOGLE_SPEECH_API_KEY):        self.language = language        self.rate = rate        self.api_key = api_key        self.retries = retries    def __call__(self, data):        try:            for _r in range(self.retries):                url = GOOGLE_SPEECH_API_URL.format(lang=self.language, key=self.api_key)                headers = {"Content-Type": "audio/x-flac; rate=%d" % self.rate}                try:                    resp = requests.post(url, data=data, headers=headers)                except requests.exceptions.ConnectionError:                    continue                for line in resp.content.decode('utf-8').split("\n"):                    try:                        line = json.loads(line)                        line = line['result'][0]['alternative'][0]['transcript']                        xxx = line[:1].upper() + line[1:]                        return xxx                    except:                        continue        except ValueError:            returndef extract_audio(filename, channels=1, rate=16000):    temp = Path(filename).stem + ".wav"    if not os.path.isfile(filename):        print("Tệp tin không tồn tại: {0}".format(filename))        raise Exception("Sai đường dẫn: {0}".format(filename))    ff = FFmpeg(        inputs={filename: None},        outputs={            temp: ["-y", "-ac", str(channels), "-ar", str(rate), "-loglevel", "error"]}    )    ff.run()    return temp, rateclass FLACConverter(object):    def __init__(self, source_path, include_before=0.25, include_after=0.25):        self.source_path = source_path        self.include_before = include_before        self.include_after = include_after    def __call__(self, region):        try:            index, start, end = region            start = max(0, start - self.include_before)            end += self.include_after            _fn = RESULT_AUDIO + "/" + Path(self.source_path).stem            if not os.path.exists(_fn):                os.mkdir(_fn)            temp = _fn + "/" + Path(self.source_path).stem + "_" + str(index) + ".flac"            ff = FFmpeg(                inputs={self.source_path: None},                outputs={                    temp: ["-y", "-ss", str(start), "-t", str(end - start), "-loglevel", "error"]}            )            ff.run()            return open(temp, 'rb').read()        except ValueError as err:            print(err)            returndef main():    parser = argparse.ArgumentParser()    parser.add_argument('source_path', help="Đường dẫn tới file video/audio", nargs='?')    parser.add_argument('-o', '--output',                        help="Thư mục lưu file phụ đề (mặc định lưu tại thư mục chứa file thực thi)")    parser.add_argument('-S', '--stt-language', help="Ngôn ngữ nhận dạng", default="en")    args = parser.parse_args()    if not args.source_path:        print("Vui lòng nhập đường dẫn video/ audio.")        return 1    if args.stt_language not in LANGUAGE_CODES.keys():        print("Không hỗ trợ nhận dạng ngôn ngữ này.")        return 1    # start = timeit.default_timer()    audio_filename, audio_rate = extract_audio(args.source_path)    regions = find_speech_regions(audio_filename)    pool = multiprocessing.Pool(10)    converter = FLACConverter(source_path=audio_filename)    stt = SpeechRecognizer(language=args.stt_language, rate=audio_rate, api_key=GOOGLE_SPEECH_API_KEY)    transcripts = []    if regions:        widgets = ["Xử lý âm thanh: ", Percentage(), ' ', ETA()]        pbar = ProgressBar(widgets=widgets, maxval=len(regions)).start()        extracted_regions = []        for i, extracted_region in enumerate(pool.imap(converter, regions)):            extracted_regions.append(extracted_region)            pbar.update(i)        pbar.finish()        widgets = ["Nhận dạng: ", Percentage(), ' ', ETA()]        pbar = ProgressBar(widgets=widgets, maxval=len(regions)).start()        for i, transcript in enumerate(pool.imap(stt, extracted_regions)):            transcripts.append(transcript)            pbar.update(i)        pbar.finish()    print("Tạo file phụ đề...")    timed_subtitles = []    # Thư mục chứa audio nhận dạng    _fn = RESULT_AUDIO + "/" + Path(audio_filename).stem    for r, t in sorted(set(zip(regions, transcripts))):        if t is not None:            timed_subtitles.append((r, t))        else:            # Xoá nó đi nếu nó không trả ra gì cả            temp = _fn + "/" + Path(audio_filename).stem + "_" + str(r[0]) + ".flac"            os.remove(temp)    # ReIndex lại file audio    # reindex_folder(_fn, Path(audio_filename).stem)    formatter = FORMATTERS.get("srt")    formatted_subtitles = formatter(timed_subtitles)    des_transcript_file = args.output    if not des_transcript_file:        base, ext = os.path.splitext(audio_filename)        des_transcript_file = "{base}.{format}".format(base=base, format="srt")    with open(des_transcript_file, 'wb') as f:        f.write(formatted_subtitles.encode("utf-8"))    # print(Path(des_transcript_file).absolute())    os.remove(audio_filename)    # stop = timeit.default_timer()    # print("Took: {0}s!".format(int(stop - start)))    return 0# TODO: Not usedef reindex_folder(path, original_name):    files = os.listdir(path)    files.sort(key=natural_keys)    i = 1    for file in files:        filename, file_extension = os.path.splitext(file)        os.rename(os.path.join(path, file), os.path.join(path, original_name + "_" + str(i) + file_extension))        i = i + 1if __name__ == '__main__':    multiprocessing.freeze_support()    sys.exit(main())