import asyncio
import httpx
import base64
import json

async def test():
    print("=" * 60)
    print("Testing Voice Conversation API")
    print("=" * 60)
    
    # Create a small silent audio file (WAV format)
    # WAV header for 1 second of silence at 16kHz, mono, 16-bit
    sample_rate = 16000
    duration = 1  # seconds
    num_samples = sample_rate * duration
    
    import struct
    wav_header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + num_samples * 2,
        b'WAVE',
        b'fmt ',
        16,
        1,   # PCM
        1,   # mono
        sample_rate,
        sample_rate * 2,
        2,
        16,
        b'data',
        num_samples * 2
    )
    audio_data = wav_header + (b'\x00\x00' * num_samples)
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    print(f"Test audio size: {len(audio_data)} bytes")
    print(f"Base64 length: {len(audio_base64)} chars")
    
    # Make request
    url = "http://localhost:8000/api/v1/voice/conversation"
    
    # Get auth token first
    auth_response = await httpx.AsyncClient().post(
        "http://localhost:8000/api/v1/auth/login",
        json={"email": "saud@gmail.com", "password": "password"}
    )
    token = auth_response.json()["access_token"]
    
    print(f"\n✅ Got auth token")
    
    # Make voice conversation request
    print(f"\nSending voice conversation request...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            url,
            json={
                "audio_base64": audio_base64,
                "context": "general",
                "use_fast_model": True
            },
            headers={"Authorization": f"Bearer {token}"}
        )
    
    print(f"\nResponse status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success!")
        print(f"Transcribed text: {data.get('transcribed_text', 'N/A')}")
        print(f"AI response text: {data.get('ai_response_text', 'N/A')[:100]}...")
        print(f"AI response audio length: {len(data.get('ai_response_audio', ''))} chars")
        
        # Check if audio is valid base64
        try:
            audio_bytes = base64.b64decode(data.get('ai_response_audio', ''))
            print(f"Decoded audio size: {len(audio_bytes)} bytes")
            print(f"Starts with RIFF: {audio_bytes[:4] == b'RIFF'}")
            print(f"First 20 bytes: {audio_bytes[:20]}")
        except Exception as e:
            print(f"❌ Failed to decode audio: {e}")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    asyncio.run(test())
