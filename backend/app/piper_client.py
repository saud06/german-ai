"""
Piper TTS client for text-to-speech synthesis
"""
import httpx
import logging
from typing import Optional
from .config import settings
import base64
import struct

logger = logging.getLogger(__name__)

class PiperClient:
    """Async Piper client wrapper for German text-to-speech"""
    
    def __init__(self):
        self.host = settings.PIPER_HOST
        self.voice = settings.PIPER_VOICE
        self.sample_rate = settings.PIPER_SAMPLE_RATE
        self.is_available = False
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def initialize(self):
        """Initialize Piper client and check availability"""
        try:
            # Piper uses Wyoming protocol, check if port is open
            response = await self.client.get(f"http://{self.host.split('//')[1].split(':')[0]}:10200/", timeout=5.0)
            self.is_available = True
            logger.info(f"✅ Piper TTS connected: {self.host} (voice: {self.voice})")
        except Exception as e:
            # Piper might not have HTTP endpoint, try TCP connection
            try:
                import socket
                host_parts = self.host.replace('http://', '').split(':')
                host = host_parts[0]
                port = int(host_parts[1]) if len(host_parts) > 1 else 10200
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    self.is_available = True
                    logger.info(f"✅ Piper TTS connected: {self.host} (voice: {self.voice})")
                else:
                    logger.warning(f"⚠️  Piper port not accessible: {e}")
            except Exception as tcp_error:
                logger.error(f"❌ Piper connection failed: {tcp_error}")
                self.is_available = False
    
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        output_format: str = "wav"
    ) -> bytes:
        """
        Synthesize text to speech using Wyoming protocol
        
        Args:
            text: Text to synthesize (German)
            voice: Voice model (default: from PIPER_VOICE config)
            output_format: Output format (wav, mp3)
        
        Returns:
            Audio bytes
        """
        if not self.is_available:
            raise Exception("Piper is not available")
        
        voice_model = voice or self.voice
        
        try:
            from wyoming.client import AsyncTcpClient
            from wyoming.tts import Synthesize
            from wyoming.audio import AudioChunk, AudioStop
            import asyncio
            
            # Parse host and port
            host_parts = self.host.replace('http://', '').split(':')
            host = host_parts[0]
            port = int(host_parts[1]) if len(host_parts) > 1 else 10200
            
            try:
                # Connect to Wyoming server
                client = AsyncTcpClient(host, port)
                await client.connect()
                
                # Send synthesize request (voice is optional, Piper uses default)
                await client.write_event(Synthesize(text=text).event())
                
                # Collect audio chunks
                audio_chunks = []
                while True:
                    event = await client.read_event()
                    if event is None:
                        break
                    
                    if AudioChunk.is_type(event.type):
                        chunk = AudioChunk.from_event(event)
                        audio_chunks.append(chunk.audio)
                    elif AudioStop.is_type(event.type):
                        break
                
                await client.disconnect()
                
                # Combine audio chunks
                audio_data = b''.join(audio_chunks)
                
                if not audio_data or len(audio_data) < 100:
                    logger.warning(f"⚠️  Piper returned no/minimal audio ({len(audio_data)} bytes)")
                    return self._generate_silence(duration=len(text) * 0.1)
                
                # Add WAV header if not present (Piper returns raw PCM)
                if not audio_data.startswith(b'RIFF'):
                    audio_data = self._add_wav_header(audio_data)
                
                logger.info(f"✅ Piper synthesized {len(audio_data)} bytes for '{text[:50]}...'")
                return audio_data
                
            except Exception as e:
                logger.error(f"Piper Wyoming error: {type(e).__name__}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return self._generate_silence(duration=len(text) * 0.1)
            
        except Exception as e:
            logger.error(f"Piper synthesis error: {e}")
            return self._generate_silence(duration=len(text) * 0.1)
    
    async def synthesize_to_base64(
        self,
        text: str,
        voice: Optional[str] = None
    ) -> str:
        """
        Synthesize text and return base64-encoded audio
        
        Args:
            text: Text to synthesize
            voice: Voice model
        
        Returns:
            Base64-encoded audio
        """
        try:
            audio_data = await self.synthesize(text, voice)
            return base64.b64encode(audio_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Base64 synthesis error: {e}")
            raise
    
    def _generate_silence(self, duration: float = 1.0) -> bytes:
        """Generate silent WAV file (fallback)"""
        sample_rate = self.sample_rate
        num_samples = int(sample_rate * duration)
        
        # WAV header
        wav_header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF',
            36 + num_samples * 2,
            b'WAVE',
            b'fmt ',
            16,  # fmt chunk size
            1,   # PCM
            1,   # mono
            sample_rate,
            sample_rate * 2,
            2,   # block align
            16,  # bits per sample
            b'data',
            num_samples * 2
        )
        
        # Silent audio data
        audio_data = b'\x00\x00' * num_samples
        
        return wav_header + audio_data
    
    def _add_wav_header(self, pcm_data: bytes) -> bytes:
        """Add WAV header to raw PCM audio data"""
        sample_rate = self.sample_rate
        num_samples = len(pcm_data) // 2  # 16-bit samples
        
        # WAV header
        wav_header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF',
            36 + len(pcm_data),
            b'WAVE',
            b'fmt ',
            16,  # fmt chunk size
            1,   # PCM
            1,   # mono
            sample_rate,
            sample_rate * 2,
            2,   # block align
            16,  # bits per sample
            b'data',
            len(pcm_data)
        )
        
        return wav_header + pcm_data
    
    async def health_check(self) -> bool:
        """Check if Piper service is healthy"""
        try:
            import socket
            host_parts = self.host.replace('http://', '').split(':')
            host = host_parts[0]
            port = int(host_parts[1]) if len(host_parts) > 1 else 10200
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            return result == 0
        except:
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

# Global Piper client instance
piper_client = PiperClient()

async def get_piper() -> PiperClient:
    """Dependency for FastAPI routes"""
    return piper_client
