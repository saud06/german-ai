import asyncio
import sys
sys.path.insert(0, '/app')

from app.piper_client import piper_client

async def test():
    print("=" * 50)
    print("Testing Piper TTS")
    print("=" * 50)
    print(f"Piper available: {piper_client.is_available}")
    print(f"Piper host: {piper_client.host}")
    
    try:
        print("\nSynthesizing 'Hallo'...")
        audio = await piper_client.synthesize("Hallo")
        print(f"✅ Audio length: {len(audio)} bytes")
        print(f"✅ Starts with RIFF: {audio.startswith(b'RIFF')}")
        print(f"✅ First 20 bytes: {audio[:20]}")
        
        # Test base64
        print("\nTesting base64 encoding...")
        audio_b64 = await piper_client.synthesize_to_base64("Hallo")
        print(f"✅ Base64 length: {len(audio_b64)} chars")
        print(f"✅ First 50 chars: {audio_b64[:50]}")
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
