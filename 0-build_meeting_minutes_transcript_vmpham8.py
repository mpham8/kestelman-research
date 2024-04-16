import os
from pydub import AudioSegment
import speech_recognition as sr
import torch
import transformers
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

transformers.logging.set_verbosity_error()

# Define the path to the folder containing your MP3 files
folder_path_audio = "audio"
folder_path_txt = "txt"


#model config
model_id = "openai/whisper-base" #WHERE TO CHANGE MODEL SIZE
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

#load model
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=30,
    batch_size=16,
    return_timestamps=True,
    torch_dtype=torch_dtype,
    device=device,
)


# Function to split audio
def split_audio(audio, target_length_in_seconds):
    """
    Splits the audio into chunks of target_length_in_seconds.
    Returns a list of audio segments.
    """
    length_of_audio = len(audio)
    start = 0
    end = target_length_in_seconds * 1000  # PyDub works in millisecs
    chunks = []

    while start < length_of_audio:
        chunks.append(audio[start:end])
        start = end
        end += target_length_in_seconds * 1000
    return chunks

target_size_bytes = 1 * 1024 * 1024  # 10MB in bytes
# Loop through all files in the folder
for filename in os.listdir(folder_path_audio):
    if filename.endswith(".mp3"):
        mp3_file_path = os.path.join(folder_path_audio, filename)
        base_wav_file_path = os.path.join(folder_path_audio, filename.replace(".mp3", ""))
        txt_file_path = os.path.join(folder_path_txt, filename.replace(".mp3", ".txt"))
        mp3_done_file_path = os.path.join(folder_path_txt, 'mp3_converted_vmpham\\', filename)
        
        # Convert MP3 to WAV
        print(f"Converting {filename} to WAV...", flush=True)
        audio = AudioSegment.from_mp3(mp3_file_path)
        
        # Calculate segment length for a target size (e.g., 10MB)
        bytes_per_second = len(audio) / len(audio) * (audio.frame_rate * audio.frame_width)
        target_length_seconds = target_size_bytes / bytes_per_second
        # Split audio if it's larger than 10MB
        if os.path.getsize(mp3_file_path) > target_size_bytes:
            chunks = split_audio(audio, target_length_seconds)
            for i, chunk in enumerate(chunks):
                segment_wav_file_path = f"{base_wav_file_path}_part_{i}.wav"
                print(f"Exporting {segment_wav_file_path}...", flush=True)
                chunk.export(segment_wav_file_path, format="wav")
                
                #Forward feed audio into Whisper model
                print(f"Running inference on {filename}")          
                text = pipe(segment_wav_file_path)


                #write output to corresponding txt file
                print(f"Transcription of {segment_wav_file_path}: Appending to {txt_file_path}", flush=True)
                with open(txt_file_path, 'a') as text_file:
                    text_file.write(text["text"] + "\n")

                os.remove(segment_wav_file_path)
                # os.remove(os.path.join(folder_path_audio, segment_wav_file_path))

                print(f"Deleted {segment_wav_file_path}")    
        else:
            # If audio is smaller than 10MB, process normally
            wav_file_path = base_wav_file_path + ".wav"
            audio.export(wav_file_path, format="wav")
            
            #Forward feed audio into Whisper model
            print(f"Running inference on {filename}")         
            text = pipe(wav_file_path)
            
            #write output to corresponding txt file
            print(f"Transcription of {filename}: Saving to {txt_file_path}")
            with open(txt_file_path, 'w') as text_file:
                text_file.write(text["text"])
                                   
            os.remove(wav_file_path)
            # os.remove(os.path.join(folder_path_audio, wav_file_path))
            print(f"Deleted {wav_file_path}")       
        
            #os.rename(mp3_file_path, mp3_done_file_path)

# # Optionally, delete the WAV files after transcription if they are no longer needed
# for wav_filename in os.listdir(folder_path):
#     if wav_filename.endswith(".wav"):
#         os.remove(os.path.join(folder_path, wav_filename))
#         print(f"Deleted {wav_filename}")
