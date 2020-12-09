import sys
sys.path.append('../')

from app.utils.diarizer.voice_encoder import VoiceEncoder
from pathlib import Path
from app.utils.diarize import Diarizer
from app.utils.transcribe import Transcriber
from app.utils.summarise import Summarizer
from app.utils.util_functions import UtilFunctions
import time
import wavio
import numpy as np

utilfunctions = UtilFunctions()

### Inputs required: Speaker names list, speaker embeddings, meeting audio path, directory to store results

def meeting_pipeline(speaker_names, speaker_embeddings, meeting_audio_path, results_storage_directory):

    current_timestamp = str(time.time())

    # To be passed to function from Views
    speaker_names = ['Manav Zota', 'Nirav Zota', 'Rashmi Zota', 'Lata Zota']
    speaker_samples = [Path('Neighbour Recordings', 'Manav Zota.wav'), Path('Neighbour Recordings', 'Nirav Zota.wav'), Path('Neighbour Recordings', 'Rashmi Zota.wav'), Path('Neighbour Recordings', 'Lata Zota.wav')]
    wav_path = Path('Neighbour Recordings', 'Everybody.wav')


    ############## Diarization ##############
    encoder = VoiceEncoder()

    diarizer = Diarizer(wav_path, speaker_names, speaker_samples, encoder)
    trimmed_audio = diarizer.preprocess_audio()
    wavio.write(results_storage_directory + 'trimmed_meeting_' + current_timestamp + '_.wav', wav, 16000, sampwidth = 2)
    segments = diarizer.diarize_audio()
    print(segments)

    ############## Transcription ##############
    transcriber = Transcriber(segments)
    transcript_multilogue, transcript_processed = transcriber.speechToText()

    try:
        filename = results_storage_directory + "Transcript_Meeting_" + current_timestamp
        utilfunctions.write_file(filename+"_multilogue.txt", "w", transcript_multilogue)
        utilfunctions.write_file(filename+"_processed.txt", "w", transcript_processed)
    except Exception as e:
        print("Error at transcript file creation:  " + str(e))


    ############## Summarization ##############
    summarizer = Summarizer(transcript_processed, summarization_tool="sumy", summarization_method="lsa", num_sentences=20, reduction_perc=80, language="english")
    summarized_text = summarizer.summarize()

    try:
        filename = results_storage_directory + "Summary_Meeting_" + current_timestamp
        utilfunctions.write_file(filename, "w", summarized_text)
    except Exception as e:
        print("Error at summary file writing:  " + str(e))

    print("Summarized Text:\n" + summarized_text)


def speaker_pipeline(speaker_name, speaker_sample, results_storage_directory):
    encoder = VoiceEncoder()
    diarizer = Diarizer(speaker_names=speaker_name, speaker_samples=speaker_sample, encoder=encoder)
    speaker_embedding = diarizer.generate_embeddings()
    np.save(results_storage_directory+'embeddings.npy', speaker_embedding)
    return