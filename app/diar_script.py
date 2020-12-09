import sys
sys.path.append('../')

from app.utils.diarize import Diarizer
from app.utils.diarizer.voice_encoder import VoiceEncoder
from pathlib import Path
from app.utils.transcribe import Transcriber
from app.utils.summarise import Summarizer
from app.utils.util_functions import UtilFunctions
import time

utilfunctions = UtilFunctions()

speaker_names = ['Manav Zota', 'Nirav Zota', 'Rashmi Zota', 'Lata Zota']
speaker_samples = [Path('Neighbour Recordings', 'Manav Zota.wav'), Path('Neighbour Recordings', 'Nirav Zota.wav'), Path('Neighbour Recordings', 'Rashmi Zota.wav'), Path('Neighbour Recordings', 'Lata Zota.wav')]
wav_path = Path('Neighbour Recordings', 'Everybody.wav')


############## Diarization ##############
encoder = VoiceEncoder()

diarizer = Diarizer(wav_path, speaker_names, speaker_samples, encoder)
trimmed_audio = diarizer.preprocess_audio()
segments = diarizer.diarize_audio()
print(segments)

############## Transcription ##############
transcriber = Transcriber(segments)
transcript_multilogue, transcript_processed = transcriber.speechToText()

try:
    filename = "Transcript_Meeting_" + str(time.time())
    utilfunctions.write_file(filename+"_multilogue.txt", "w", transcript_multilogue)
    utilfunctions.write_file(filename+"_processed.txt", "w", transcript_processed)
except Exception as e:
    print("Error at transcript file creation:  " + str(e))


############## Summarization ##############
summarizer = Summarizer(transcript_processed, summarization_tool="sumy", summarization_method="lsa", num_sentences=20, reduction_perc=80, language="english")
summarized_text = summarizer.summarize()

try:
    filename = "Summary_Meeting_" + str(time.time())
    utilfunctions.write_file(filename, "w", summarized_text)
except Exception as e:
    print("Error at summary file writing:  " + str(e))

print("Summarized Text:\n" + summarized_text)