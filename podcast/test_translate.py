# -*- coding: utf-8 -*-

from pydub import AudioSegment
from glob import glob
from math import ceil
from os.path import basename, splitext, exists
import json
import requests
import csv
import sys


mp3_file = sys.argv[1]
text_output = sys.argv[2]

WATSON_USERNAME = "YOUR USERNAME HERE"
WATSON_PASSWORD = "YOUR PASSWORD HERE"
WATSON_ENDPOINT = 'https://stream.watsonplatform.net/speech-to-text/api/v1/recognize'
WATSON_DEFAULT_PARAMS = {
    'continuous': True,
    'timestamps': True,
    'word_confidence': True,
}
WATSON_DEFAULT_HEADERS = {
    'content-type': 'audio/wav'
}

# via: http://www.propublica.org/podcast/item/how-a-reporter-pierced-the-hype-behind-theranos/
AUDIO_FILENAME = str(mp3_file)
AUDIO_SEGMENT_SECONDS = 300


'''if not exists(AUDIO_FILENAME):
    print("Downloading from", DOWNLOAD_URL)
    resp = requests.get(DOWNLOAD_URL)

    with open(AUDIO_FILENAME, 'wb') as w:
        w.write(resp.content)
        print("Wrote audio file to", AUDIO_FILENAME)
'''
# convert to WAV
with open(AUDIO_FILENAME):
    audio = AudioSegment.from_mp3(AUDIO_FILENAME)
    xs = 0
    while xs < audio.duration_seconds:
        ys = min(xs + AUDIO_SEGMENT_SECONDS, ceil(audio.duration_seconds))
        fname = str(xs).rjust(5, '0') + '-' + str(ys).rjust(5, '0') + '.wav'
        audio[xs*1000:ys*1000].export(fname, format='wav')
        print("Saved", fname)
        xs = ys

    ## Transcribe each WAV to Watson
for fname in glob("*.wav"):
    # Download watson's response
    tname = splitext(basename(fname))[0] + '.json'
    if exists(tname):
        print("Already transcribed", tname)
    else:
        print("Transcribing", fname)
        with open(fname, 'rb') as r:
            watson_response = requests.post(
                                  WATSON_ENDPOINT,
                                  data=r,
                                  auth=(WATSON_USERNAME, WATSON_PASSWORD),
                                  params=WATSON_DEFAULT_PARAMS,
                                  headers=WATSON_DEFAULT_HEADERS,
                                  stream=False
                             )
            with open(tname, 'w') as w:
                w.write(watson_response.text)
                print("Wrote transcript to", tname)


# Print out the raw transcript and word csv
rawfile = open(text_output, "w")
wordsfile = open("words.csv", "w")
csvfile = csv.writer(wordsfile)
csvfile.writerow(['word', 'confidence', 'start', 'end'])

for fname in sorted(glob("*.json")):
    with open(fname, 'r') as f:
        results = json.load(f)['results']
        for linenum, result in enumerate(results): # each result is a  line
            if result.get('alternatives'): # each result may have many alternatives
                # just pick best alternative
                lineobj = result.get('alternatives')[0]
    #            rawfile.writeline(lineobj['transcript'])
                word_timestamps = lineobj['timestamps']
                if word_timestamps:
                    rawfile.write(lineobj['transcript'] + "\n")

                    word_confidences = lineobj['word_confidence']
                    for idx, wordts in enumerate(word_timestamps):
                        txt, tstart, tend = wordts
                        confidence = round(100 * word_confidences[idx][1])
                        csvfile.writerow([txt, confidence, tstart, tend])


rawfile.close()
wordsfile.close()
