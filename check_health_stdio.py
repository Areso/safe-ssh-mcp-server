import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Define how to launch your server script
SERVER_COMMAND = "python"
SERVER_ARGS = ["mcp_ssh.py"]  # Adjust path if mcp_ssh.py is in another directory

async def check_server():
    print(f"🔌 Spawning server process via stdio ({SERVER_COMMAND} {' '.join(SERVER_ARGS)})...")
    
    # Set up the execution parameters
    server_params = StdioServerParameters(
        command=SERVER_COMMAND,
        args=SERVER_ARGS,
        env=os.environ.copy()  # Passes your current environment variables down to the server
    )
    
    try:
        # stdio_client launches the script as a subprocess
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Perform the MCP handshake
                await session.initialize()
                
                # Fetch tools to verify functionality
                result = await session.list_tools()
                
                print(f"\n✅ SUCCESS! Server is healthy.")
                print(f"   Found {len(result.tools)} tool(s):")
                for tool in result.tools:
                    print(f"   - {tool.name}: {tool.description}")
                    
    except Exception as e:
        print(f"\n❌ FAILED to initialize server.")
        print(f"   Error: {e}")
        print("   (Ensure Python can locate 'mcp_ssh.py' and your dependencies are active.)")

if __name__ == "__main__":
    # Requires: pip install mcp
    asyncio.run(check_server())