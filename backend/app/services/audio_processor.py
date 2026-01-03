import os
import tempfile
import librosa
import numpy as np
from pydub import AudioSegment
from pydub.utils import make_chunks
import logging
from typing import List, Tuple, Optional
import aiofiles
import asyncio

logger = logging.getLogger(__name__)


class AudioProcessor:
    def __init__(self, sample_rate: int = 16000, chunk_duration_ms: int = 1000):
        self.sample_rate = sample_rate
        self.chunk_duration_ms = chunk_duration_ms
        
    async def save_uploaded_audio(self, audio_data: bytes, filename: str) -> str:
        """Save uploaded audio data to temporary file"""
        try:
            # Create temp directory if it doesn't exist
            temp_dir = os.path.join(tempfile.gettempdir(), "ai_call_audio")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Generate unique filename
            file_path = os.path.join(temp_dir, filename)
            
            # Save audio data
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(audio_data)
            
            logger.info(f"Audio saved to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            raise
    
    def convert_to_wav(self, input_path: str, output_path: str = None) -> str:
        """Convert audio file to WAV format for processing"""
        try:
            if output_path is None:
                base_name = os.path.splitext(input_path)[0]
                output_path = f"{base_name}_converted.wav"
            
            # Load audio with pydub (supports many formats)
            audio = AudioSegment.from_file(input_path)
            
            # Convert to mono and set sample rate
            audio = audio.set_channels(1)
            audio = audio.set_frame_rate(self.sample_rate)
            
            # Export as WAV
            audio.export(output_path, format="wav")
            
            logger.info(f"Audio converted to WAV: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting audio to WAV: {e}")
            raise
    
    def enhance_audio(self, input_path: str, output_path: str) -> str:
        """Enhance audio quality with basic normalization"""
        try:
            # Load audio with pydub
            audio = AudioSegment.from_wav(input_path)
            
            # Basic audio enhancement:
            # 1. Normalize volume
            normalized_audio = audio.normalize()
            
            # 2. Apply basic noise reduction (simple high-pass filter)
            # Remove frequencies below 80Hz (typical noise)
            filtered_audio = normalized_audio.high_pass_filter(80)
            
            # Export enhanced audio
            filtered_audio.export(output_path, format="wav")
            
            logger.info(f"Audio enhanced: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error enhancing audio {input_path}: {e}")
            # Fallback: just copy the input to output
            import shutil
            shutil.copy2(input_path, output_path)
            return output_path
    
    async def process_audio_file(self, audio_path: str) -> dict:
        """Process audio file for hackathon endpoint - convert and enhance"""
        try:
            # Step 1: Convert to WAV
            base_name = os.path.splitext(audio_path)[0]
            wav_path = f"{base_name}_converted.wav"
            converted_path = self.convert_to_wav(audio_path, wav_path)
            
            # Step 2: Enhance audio (basic noise reduction/normalization)
            enhanced_path = f"{base_name}_converted_enhanced.wav"
            enhanced_audio_path = self.enhance_audio(converted_path, enhanced_path)
            
            logger.info(f"Audio processed: {enhanced_audio_path}")
            return {
                "original_path": audio_path,
                "converted_path": converted_path,
                "enhanced_path": enhanced_audio_path,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error processing audio file {audio_path}: {e}")
            return {
                "original_path": audio_path,
                "enhanced_path": audio_path,  # Fallback to original
                "status": "error",
                "error": str(e)
            }
    
    def split_audio_chunks(self, audio_path: str) -> List[str]:
        """Split audio into smaller chunks for processing"""
        try:
            audio = AudioSegment.from_wav(audio_path)
            chunks = make_chunks(audio, self.chunk_duration_ms)
            
            chunk_paths = []
            base_name = os.path.splitext(audio_path)[0]
            
            for i, chunk in enumerate(chunks):
                if len(chunk) < 100:  # Skip very short chunks
                    continue
                    
                chunk_path = f"{base_name}_chunk_{i:03d}.wav"
                chunk.export(chunk_path, format="wav")
                chunk_paths.append(chunk_path)
            
            logger.info(f"Audio split into {len(chunk_paths)} chunks")
            return chunk_paths
            
        except Exception as e:
            logger.error(f"Error splitting audio: {e}")
            raise
    
    def analyze_audio_properties(self, audio_path: str) -> dict:
        """Analyze audio properties like duration, volume, etc."""
        try:
            # Load with librosa for detailed analysis
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Basic properties
            duration = len(y) / sr
            
            # RMS energy (volume indicator)
            rms = librosa.feature.rms(y=y)[0]
            avg_volume = np.mean(rms)
            
            # Zero crossing rate (speech activity indicator)
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            avg_zcr = np.mean(zcr)
            
            # Spectral centroid (brightness/clarity)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            avg_spectral_centroid = np.mean(spectral_centroids)
            
            # Detect speech/silence segments
            speech_segments = self._detect_speech_segments(y, sr)
            
            return {
                "duration": duration,
                "sample_rate": sr,
                "avg_volume": float(avg_volume),
                "avg_zero_crossing_rate": float(avg_zcr),
                "avg_spectral_centroid": float(avg_spectral_centroid),
                "speech_segments": speech_segments,
                "total_speech_time": sum([seg[1] - seg[0] for seg in speech_segments]),
                "silence_ratio": 1 - (sum([seg[1] - seg[0] for seg in speech_segments]) / duration)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing audio properties: {e}")
            return {"error": str(e)}
    
    def _detect_speech_segments(self, y: np.ndarray, sr: int, 
                               frame_length: int = 2048, 
                               hop_length: int = 512) -> List[Tuple[float, float]]:
        """Detect speech vs silence segments using energy thresholding"""
        try:
            # Calculate frame-wise RMS energy
            rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
            
            # Dynamic threshold based on audio characteristics
            threshold = np.percentile(rms, 30)  # Use 30th percentile as threshold
            
            # Convert frame indices to time
            times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
            
            # Find speech segments
            speech_frames = rms > threshold
            segments = []
            
            in_speech = False
            start_time = 0
            
            for i, is_speech in enumerate(speech_frames):
                if is_speech and not in_speech:
                    # Start of speech segment
                    start_time = times[i]
                    in_speech = True
                elif not is_speech and in_speech:
                    # End of speech segment
                    end_time = times[i]
                    if end_time - start_time > 0.1:  # Minimum segment length
                        segments.append((start_time, end_time))
                    in_speech = False
            
            # Handle case where audio ends during speech
            if in_speech:
                segments.append((start_time, times[-1]))
            
            return segments
            
        except Exception as e:
            logger.error(f"Error detecting speech segments: {e}")
            return []
    
    def enhance_audio_quality(self, audio_path: str, output_path: str = None) -> str:
        """Apply basic audio enhancement for better transcription"""
        try:
            if output_path is None:
                base_name = os.path.splitext(audio_path)[0]
                output_path = f"{base_name}_enhanced.wav"
            
            # Load audio
            audio = AudioSegment.from_wav(audio_path)
            
            # Normalize volume
            audio = audio.normalize()
            
            # Apply high-pass filter to reduce low-frequency noise
            audio = audio.high_pass_filter(80)
            
            # Apply low-pass filter to reduce high-frequency noise
            audio = audio.low_pass_filter(8000)
            
            # Export enhanced audio
            audio.export(output_path, format="wav")
            
            logger.info(f"Audio enhanced: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error enhancing audio: {e}")
            return audio_path  # Return original if enhancement fails
    
    async def cleanup_temp_files(self, file_paths: List[str]):
        """Clean up temporary audio files"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Cleaned up: {file_path}")
            except Exception as e:
                logger.warning(f"Could not clean up {file_path}: {e}")
    
    def validate_audio_file(self, file_path: str) -> bool:
        """Validate if audio file is readable and has content"""
        try:
            audio = AudioSegment.from_file(file_path)
            return len(audio) > 0
        except Exception as e:
            logger.error(f"Audio validation failed: {e}")
            return False
