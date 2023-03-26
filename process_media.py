import io
import wave
import tensorflow as tf
import tensorflow_io as tfio
from pydub import AudioSegment
from transformers import AutoProcessor, TFWhisperForConditionalGeneration

# tf.config.run_functions_eagerly(True)

class MediaProcessor:

    def __init__(self):
        self.processor = AutoProcessor.from_pretrained("openai/whisper-tiny.en")
        self.model = TFWhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny.en")

    def load_wav_16k_mono(self, file_bytes):
        """ Load a WAV file, convert it to a float tensor, resample to 16 kHz single-channel audio. """
        wav, sample_rate = tf.audio.decode_wav(
            file_bytes,
            desired_channels=1)
        wav = tf.squeeze(wav, axis=-1)
        sample_rate = tf.cast(sample_rate, dtype=tf.int64)
        wav = tfio.audio.resample(wav, rate_in=sample_rate, rate_out=16000)
        return wav.numpy()

    def get_text_from_audio(self, resampled_audio_data):
        # Split the resampled audio data into 30-second chunks
        chunk_size = 30 * 16000
        audio_chunks = [resampled_audio_data[i:i+chunk_size] for i in range(0, len(resampled_audio_data), chunk_size)]

        text = []
        for chunk in audio_chunks:
            inputs = self.processor(chunk, sampling_rate=16000, return_tensors="tf").input_features
            predicted_ids = self.model.generate(inputs, max_new_tokens=500)
            transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)
            text.append(transcription[0])
        
        return " ".join(text)
    
    def get_audio_from_video(self, video_buffer):
        buffer = io.BytesIO(video_buffer)
        video_file = AudioSegment.from_file(buffer)
        audio = video_file.set_channels(1)
        with io.BytesIO() as wav_buffer:
            audio.export(wav_buffer, format="wav")
            wav_bytes = wav_buffer.getvalue()
        return wav_bytes
    
    def get_wav_from_audio(self, audio_buffer):
        buffer = io.BytesIO(audio_buffer)
        audio_file = AudioSegment.from_mp3(buffer)
        raw_data = audio_file.raw_data
        with io.BytesIO() as wav_buffer:
            with wave.open(wav_buffer, "wb") as wav_file:
                wav_file.setnchannels(audio_file.channels)
                wav_file.setsampwidth(audio_file.sample_width)
                wav_file.setframerate(audio_file.frame_rate)
                wav_file.writeframes(raw_data)
            wav_bytes = wav_buffer.getvalue()
        return wav_bytes
    
    def process_audio(self, audio_bytes):
        resampled_audio_data = self.load_wav_16k_mono(audio_bytes)
        return self.get_text_from_audio(resampled_audio_data)
    
    def process_video(self, buffer):
        audio_bytes = self.get_audio_from_video(buffer)
        return self.process_audio(audio_bytes)

