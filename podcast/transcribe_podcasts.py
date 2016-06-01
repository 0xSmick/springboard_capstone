# -*- coding: utf-8 -*-
"""
Created on Fri May 27 14:55:33 2016

@author: sheldon
"""

from pydub import AudioSegment
import glob
from math import ceil
import os
import json
import requests
import csv
import sys
import speech_recognition as sr
r = sr.Recognizer()


def transcribe_mp3(AUDIO_FILENAME, AUDIO_SEGMENT_SECONDS):
    output_file_name = "{}_translation.txt".format(AUDIO_FILENAME)
    #fuction to transform mp3 file to wav for transcription
    
    def transform_mp3_wav(AUDIO_FILENAME, AUDIO_SEGMENT_SECONDS):
        filename = AUDIO_FILENAME.replace('.mp3','')
        with open(AUDIO_FILENAME):
            audio = AudioSegment.from_mp3(AUDIO_FILENAME)
            xs = 0
            while xs < audio.duration_seconds:
                ys = min(xs + AUDIO_SEGMENT_SECONDS, ceil(audio.duration_seconds))
                fname = str(xs).rjust(5, '0') + '-' + str(ys).rjust(5, '0') + '.wav'
                audio[xs*1000:ys*1000].export(os.getcwd() + '/' + filename + fname, format='wav')
                print("Saved", fname)
                xs = ys
    transform_mp3_wav(AUDIO_FILENAME, 300)
    wav_filename = AUDIO_FILENAME.replace('.mp3','.wav')
    wav_list = glob.glob('*.wav')
    wav_list = filter(lambda x: '.mp3' not in x, wav_list)
    trans_list = []
    transcription = None
    for wav_file in wav_list: 
        print 'transcribing: ' + wav_file
        with sr.AudioFile(wav_file) as source:
            audio = r.record(source)
            transcription = r.recognize_sphinx(audio)
            print 'transcription completed'
        trans_list.extend(transcription)
        
    transcription = ''.join(trans_list)
    
    for f in wav_list:
        os.remove(f)
    
    file = open(output_file_name,'w')
    file.write(transcription)
    file.close()

for mp3_file in os.listdir(os.getcwd()):
    print 'beginning transcription: ',mp3_file
    transcribe_mp3(mp3_file, 300)
    print 'transcription complete: ',mp3_file