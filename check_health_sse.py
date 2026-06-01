import asyncio
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

# Make sure this matches your config.ini
SERVER_URL = "http://127.0.0.1:4747/sse"

async def check_server():
    print(f"🔌 Connecting to {SERVER_URL}...")
    try:
        async with sse_client(SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Ask server for tools
                result = await session.list_tools()
                
                print(f"\n✅ SUCCESS! Server is healthy.")
                print(f"   Found {len(result.tools)} tool(s):")
                for tool in result.tools:
                    print(f"   - {tool.name}: {tool.description}")
                    
    except Exception as e:
        print(f"\n❌ FAILED to connect.")
        print(f"   Error: {e}")
        print("   (Ensure mcp_ssh.py is running and port matches config.ini)")

if __name__ == "__main__":
    # Requires: pip install mcp httpx
    asyncio.run(check_server())