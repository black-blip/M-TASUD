from scipy.ndimage.morphology import binary_dilation
from app.utils.diarizer.hparams import *
# from scipy.io.wavfile import write
import wavio
from app.utils.diarizer import *
from pathlib import Path
from typing import Optional, Union, List
import numpy as np
import webrtcvad
import librosa
import struct
import time


class Diarizer():
    def __init__(self, fpath_or_wav: Union[str, Path, np.ndarray], speaker_names: List[str], speaker_samples: List[Union[str, Path, np.ndarray]], encoder):
        """
        :param fpath_or_wav: either a filepath to an audio file (many extensions are supported, not
        just .wav), either the waveform as a numpy array of floats.
        :param speaker_names: a list consisting the names of atleast all the speakers present in the file
        :param speaker_samples: a list consisting of voice samples of corresponding speakers in speaker_names
        :param encoder: the live object of the VoiceEncoder class
        """
        self.fpath_or_wav = fpath_or_wav
        self.speaker_names = speaker_names
        self.speaker_samples = speaker_samples
        self.encoder = encoder
        self.sampling_rate = 16000


    def preprocess_audio(self):
        """
        Applies preprocessing operations to a waveform either on disk or in memory such that
        The waveform will be resampled to match the data hyperparameters.

        :param fpath_or_wav: either a filepath to an audio file (many extensions are supported, not
        just .wav), either the waveform as a numpy array of floats.
        """
        if isinstance(self.fpath_or_wav, str) or isinstance(self.fpath_or_wav, Path):
            wav, source_sr = librosa.load(str(self.fpath_or_wav), sr = None)
        else:
            wav = fpath_or_wav

        speaker_voice_samples = []
        for sample in self.speaker_samples:
            if isinstance(sample, str) or isinstance(sample, Path):
                new, new_source_sr = librosa.load(str(sample), sr = None)
            else:
                new = sample
            # speaker_voice_samples.append(new[0 * 16000: 7 * 16000])
            speaker_voice_samples.append(new)

        # Apply the preprocessing: normalize volume and shorten long silences
        wav = normalize_volume(wav, audio_norm_target_dBFS, increase_only=True)
        wav = trim_silences(wav)

        final_speaker_samples = []
        for sample in speaker_voice_samples:
            new_sample = normalize_volume(sample, audio_norm_target_dBFS, increase_only=True)
            new_sample = trim_silences(sample)
            final_speaker_samples.append(new_sample)

        self.speaker_samples = final_speaker_samples
        self.wav = wav
        # wavio.write('trimmed_test_' + str(time.time()) + '_.wav', wav, 16000, sampwidth = 2)
        return wav


    def diarize_audio(self):
        """
        Extracts voice embeddings of speakers from their segments and the audio file provided.
        Compares the voice embedding of a particular frame with the ones generated and on basis of
        similarity, generates probabolity values of the frame having a particular speaker.
        """
        _, cont_embeds, wav_splits = self.encoder.embed_utterance(self.wav, return_partials=True, rate=32)

        speaker_embeds = [self.encoder.embed_utterance(speaker_wav) for speaker_wav in self.speaker_samples]
        similarity_dict = {name: cont_embeds @ speaker_embed for name, speaker_embed in
                           zip(self.speaker_names, speaker_embeds)}

        speaker_list = []
        speaker_probabilies = []
        for speaker in similarity_dict.keys():
            speaker_list.append(speaker)
            speaker_probabilies.append(similarity_dict[speaker])

        current_speaker = ""
        speaker_start = 0
        speaker_end = 0
        speaker_segments = []
        silent_wav = np.zeros(16000*4)

        # samples_per_frame = 160 # sampling_rate * mel_window_step / 1000
        # rate = 16 # from above function parameter -> embed_utterance
        # frame_step = 6 # sampling_rate / rate) / samples_per_frame
        # n_frames = int(np.ceil((len(wav) + 1) / samples_per_frame))
        # steps = max(1, n_frames - partials_n_frames + frame_step + 1)
        # steps_time = []
        # for i in range(0, steps, frame_step):
        #     wav_range = [i, i + partials_n_frames] * samples_per_frame
        #     steps_time.append(wav_range / 16000)

        wav_range = [int((s.start + s.stop) / 2) for s in wav_splits]
        # wav_range_2 = [[s.start, s.stop] for s in wav_splits]
        for i in range(0, len(speaker_probabilies[0])):
            max_prob = 0
            probable_speaker = None
            for j in range(0, len(speaker_list)):
                if speaker_probabilies[j][i] >= max_prob:
                    max_prob = speaker_probabilies[j][i]
                    probable_speaker = speaker_list[j]
                    if i == 0:
                        current_speaker = probable_speaker
            if current_speaker != probable_speaker:
                file_start = wav_range[speaker_start]
                file_end = wav_range[speaker_end]
                file_path = current_speaker+str(speaker_start)+str(speaker_end)+'.wav'
                wavio.write(file_path, np.concatenate((silent_wav, self.wav[file_start:file_end], silent_wav)), 16000, sampwidth = 2)
                speaker_segments.append([current_speaker, wav_range[speaker_start], wav_range[speaker_end], file_path])
                speaker_start = i
                current_speaker = probable_speaker
            speaker_end += 1
        
        file_path = probable_speaker+str(speaker_start)+str(speaker_end)+'.wav'
        wavio.write(file_path, np.concatenate((silent_wav, self.wav[wav_range[speaker_start]: wav_range[len(speaker_probabilies[0])-1]], silent_wav)), 16000, sampwidth = 2)
        speaker_segments.append([probable_speaker, wav_range[speaker_start], wav_range[len(speaker_probabilies[0])-1], file_path])

        return speaker_segments

    def generate_embeddings(self):
        speaker_embeds = self.encoder.embed_utterance(self.speaker_samples)
        return speaker_embeds
