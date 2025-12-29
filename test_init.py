import asyncio
import sys
sys.path.insert(0, '/app')

from app.piper_client import piper_client

async def test():
    print("=" * 50)
    print("Testing Piper Initialization")
    print("=" * 50)
    print(f"Before init - is_available: {piper_client.is_available}")
    print(f"Piper host: {piper_client.host}")
    
    print("\nCalling initialize()...")
    await piper_client.initialize()
    
    print(f"\nAfter init - is_available: {piper_client.is_available}")
    
    if piper_client.is_available:
        print("\n✅ Piper is available! Testing synthesis...")
        audio = await piper_client.synthesize("Hallo")
        print(f"✅ Audio length: {len(audio)} bytes")
        print(f"✅ Starts with RIFF: {audio.startswith(b'RIFF')}")
    else:
        print("\n❌ Piper is NOT available after initialization")

if __name__ == "__main__":
    asyncio.run(test())
