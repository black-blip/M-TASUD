import speech_recognition as sr
import time
import os

class Transcriber():

    def __init__(self, speaker_segments):
        self.speaker_segments = speaker_segments

    def speechToText(self):

        r = sr.Recognizer()
        transcript_multilogue = ""
        transcript_processed = ""
        transcribed_text = ""

        for speaker_segment in self.speaker_segments:
            current_speaker, speaker_start, speaker_stop, file_path = speaker_segment
            
            with sr.AudioFile(file_path) as source:
                r.adjust_for_ambient_noise(source)
                audio = r.record(source)

            try:
                response = r.recognize_google(audio, language = 'en-IN', show_all = True)

                if len(response)>0 and response["alternative"] is not None and len(response["alternative"])>0:
                    transcribed_text =  response["alternative"][0]["transcript"]
                else:
                    transcribed_text = ""

            except Exception as e:
                print("Error at 1 :  " + str(e))
                transcribed_text = ""

            if len(transcribed_text.strip()) > 0:
                transcript_multilogue += current_speaker + ": " + transcribed_text + ".\n\n"
                transcript_processed += current_speaker  + " said, " + "\"" + transcribed_text + ".\"\n"
            
            if os.path.exists(file_path):
                os.remove(file_path)

        # try:
        #     filename = "Meeting_" + str(time.time())
        #     with open(filename+"_multilogue.txt", "w") as multilogue_file:
        #         multilogue_file.write(transcript_multilogue)
        #     with open(filename+"_processed.txt", "w") as processed_file:
        #         processed_file.write(transcript_processed)
        # except Exception as e:
        #     print("Error at 2 :  " + str(e))

        return transcript_multilogue, transcript_processed