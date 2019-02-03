import io
import os

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from scipy.io import wavfile

def createURI(bucket_name, file_path):
    return "gs://{}/{}".format(bucket_name,file_path)

def transcribe_gcs(gcs_uri):
    """Asynchronously transcribes the audio file specified by the gcs_uri."""
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    audio = types.RecognitionAudio(uri=gcs_uri)
    config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
#     sample_rate_hertz=8000,
    language_code='en-US')

    operation = client.long_running_recognize(config, audio)

    print('Waiting for operation to complete...')
    response = operation.result(timeout=90)

    output_list = []
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print(u'Transcript: {}'.format(result.alternatives[0].transcript))
        print('Confidence: {}'.format(result.alternatives[0].confidence))
        output_list.append(result.alternatives[0].transcript)

    output =""

    for out in output_list:
        output+=out
        output+="."
    return output

def cut_data(wav_file):
    fs, data = wavfile.read(wav_file)
    wavfile.write('mono_{}.wav'.format(wav_file),fs, data[:,0])
    return 'mono_{}.wav'.format(wav_file)

def generate_analysis(bucket_name,filepath):
    return transcribe_gcs(createURI(bucket_name,filepath))
