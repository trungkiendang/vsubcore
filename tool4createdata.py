import os
import sys
from pathlib import Path

import pysrt
from ffmpy import FFmpeg

from vsub import extract_audio

if __name__ == '__main__':
    if sys.argv.__len__() != 3:
        print('Syntax: xxx.py [audio/video] [srt_file]')
        sys.exit(1)
    srt_file = pysrt.open(sys.argv[2])
    media = sys.argv[1]
    # Tạo folder lưu trữ Audio
    folder = Path(media).stem
    text_file = folder + '.txt'
    if not os.path.exists(folder):
        os.mkdir(folder)
    lst_text = []
    lst_time = []
    print('Process subtitle...')
    for t in srt_file:
        lst_text.append(t.text)
        lst_time.append([t.index, t.start, t.end, t.duration.seconds])
    # Ghi xuống file
    print('Write text to file...')
    with open(text_file, 'w', encoding='utf-8') as out:
        for t in lst_text:
            out.write(t + '\n')
    print('Write done: {}'.format(text_file))
    # Xử lý audio/video
    # Convert to wav mono 16000
    print('Process audio, write to folder: {}'.format(folder))
    audio_filename, audio_rate = extract_audio(filename=media)
    # Tách Audio
    for x in lst_time:
        index, start, end, dur = x
        if index % 10 == 0:
            print('Process audio {}/{}'.format(index, lst_time.__len__()))
        file_out = folder + '/' + folder + '-' + str(index) + '.wav'
        ff = FFmpeg(
            inputs={media: None},
            outputs={
                file_out: ["-ss", str(start).replace(',', '.'), "-to", str(end).replace(',', '.'),
                           "-y", "-loglevel", "error"]}
        )
        ff.run()
    os.remove(audio_filename)
    print('done!')
