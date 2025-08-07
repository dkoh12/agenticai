import asyncio
import json
import sys
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import httpx


class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama3.2"
    
    async def generate(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate a response using Ollama"""
        # Convert messages to Ollama format
        prompt = self._convert_messages_to_prompt(messages)
        
        # Add tool information to system prompt if tools are available
        if tools:
            tool_descriptions = self._format_tools_for_prompt(tools)
            prompt = f"You have access to the following tools:\n{tool_descriptions}\n\nTo use a tool, respond with a JSON object in this exact format:\n{{\n  \"tool_use\": {{\n    \"name\": \"tool_name\",\n    \"arguments\": {{\"param\": \"value\"}}\n  }}\n}}\n\nTo respond normally without tools (especially when you have TOOL_RESULT information to work with), use this format:\n{{\n  \"response\": \"your normal text response here incorporating any tool results\"\n}}\n\nWhen you see TOOL_RESULT in the conversation, use that information to provide a comprehensive answer to the user's question. Do not call tools again unless you need additional information.\n\n{prompt}"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",  # Force JSON output
                "options": {
                    "temperature": 0.7,
                }
            }
        else:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                }
            }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()

                # If tools were provided, expect JSON response
                if tools:
                    try:
                        # Parse the JSON response from Ollama
                        ollama_response = json.loads(result["response"])
                        
                        if "tool_use" in ollama_response:
                            # Return structured tool use
                            return {
                                "content": [{"type": "tool_use", "tool_use": ollama_response["tool_use"]}]
                            }
                        elif "response" in ollama_response:
                            # Return normal text response
                            return {
                                "content": [{"type": "text", "text": ollama_response["response"]}]
                            }
                        else:
                            # Fallback to raw response
                            return {
                                "content": [{"type": "text", "text": result["response"]}]
                            }
                    except json.JSONDecodeError:
                        # If JSON parsing fails, treat as regular text
                        return {
                            "content": [{"type": "text", "text": result["response"]}]
                        }
                else:
                    # No tools, return regular text response
                    return {
                        "content": [{"type": "text", "text": result["response"]}]
                    }
            except Exception as e:
                print(f"Error calling Ollama: {e}")
                return {
                    "content": [{"type": "text", "text": "Sorry, I encountered an error while processing your request."}]
                }
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, Any]]) -> str:
        """Convert message format to simple prompt"""
        prompt_parts = []
        for msg in messages:
            print("msg:", msg)

            role = msg["role"]
            content = msg["content"]
            
            if isinstance(content, str):
                # Special handling for tool role to make it clear it's a tool result
                if role == "tool":
                    prompt_parts.append(f"TOOL_RESULT: {content}")
                else:
                    prompt_parts.append(f"{role.upper()}: {content}")
            elif isinstance(content, list):
                # Handle complex content (like tool results)
                text_parts = []
                for item in content:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            text_parts.append(item["text"])
                        elif item.get("type") == "tool_use":
                            # Convert tool use back to readable format
                            tool_info = item["tool_use"]
                            text_parts.append(f"Used tool {tool_info['name']} with arguments: {tool_info['arguments']}")
                        elif item.get("type") == "tool_result":
                            text_parts.append(f"Tool result: {item.get('content', '')}")
                    else:
                        text_parts.append(str(item))
                prompt_parts.append(f"{role.upper()}: {' '.join(text_parts)}")
        
        return "\n\n".join(prompt_parts)
    
    def _format_tools_for_prompt(self, tools: List[Dict[str, Any]]) -> str:
        """Format tools for inclusion in prompt"""
        tool_descriptions = []
        for tool in tools:
            name = tool["name"]
            description = tool["description"]
            schema = tool.get("input_schema", {})
            
            tool_desc = f"- {name}: {description}"
            if schema.get("properties"):
                params = []
                for param, details in schema["properties"].items():
                    param_desc = f"{param} ({details.get('type', 'any')})"
                    if details.get("description"):
                        param_desc += f": {details['description']}"
                    params.append(param_desc)
                tool_desc += f"\n  Parameters: {', '.join(params)}"
            
            tool_descriptions.append(tool_desc)
        
        return "\n".join(tool_descriptions)


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.ollama = OllamaClient()

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using Ollama and available tools with support for multiple tool calls"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name, # function name
            "description": tool.description, # function doc string
            "input_schema": tool.inputSchema # function arguments and types
        } for tool in response.tools]

        max_iterations = 10  # Safety upper bound
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
            
            # Call Ollama with current messages and available tools
            response = await self.ollama.generate(
                messages=messages,
                tools=available_tools
            )

            print(f"\nOllama response (iteration {iteration}):")
            print(response)
            print()

            # Check if the response contains tool use or just text
            has_tool_use = False
            assistant_content = []
            
            for content in response["content"]:
                if content["type"] == "text":
                    text = content["text"]
                    assistant_content.append(text)
                elif content["type"] == "tool_use":
                    has_tool_use = True
                    tool_use = content["tool_use"]
                    tool_name = tool_use["name"]
                    tool_args = tool_use["arguments"]

                    try:
                        # Execute tool call
                        result = await self.session.call_tool(tool_name, tool_args)

                        print(f"\nCalling tool: {tool_name} with args: {tool_args}")
                        print("Tool result:", result)
                        print()

                        # Add assistant's tool use to messages (this represents what the assistant decided to do)
                        messages.append({
                            "role": "assistant", 
                            "content": [{"type": "tool_use", "tool_use": {"name": tool_name, "arguments": tool_args}}]
                        })
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "content": f"Tool result: {result.content}"
                        })

                    except Exception as e:
                        print(f"Error executing tool {tool_name}: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        
                        # Add assistant's tool use attempt to messages
                        messages.append({
                            "role": "assistant",
                            "content": [{"type": "tool_use", "tool_use": {"name": tool_name, "arguments": tool_args}}]
                        })
                        
                        # Add error to messages so LLM can handle it
                        messages.append({
                            "role": "tool",
                            "content": f"Error: {str(e)}"
                        })

            # If no tool use was detected, we're done - return the text response
            if not has_tool_use:
                final_response = "\n".join(assistant_content)
                # print(f"No tool use detected. Final response: {final_response}")
                return final_response
            
            # If we used tools, continue the loop to see if LLM wants to use more tools
            print(f"Tool calls completed in iteration {iteration}. Continuing to next iteration...")

        # If we hit max iterations, make one final call without tools to get a summary
        print(f"\nReached max iterations ({max_iterations}). Getting final response...")
        final_response = await self.ollama.generate(
            messages=messages + [{
                "role": "user",
                "content": "Please provide a final summary response based on all the tool results above."
            }],
            tools=None  # No tools for final summary
        )
        
        final_text = []
        for content in final_response["content"]:
            if content["type"] == "text":
                final_text.append(content["text"])
        
        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\nResponse:")
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        print("Example: python client.py weather.py")
        sys.exit(1)

    # Check if Ollama is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/version", timeout=5.0)
            if response.status_code != 200:
                print("Error: Ollama is not running. Please start Ollama first.")
                print("Run: ollama serve")
                sys.exit(1)
    except Exception:
        print("Error: Cannot connect to Ollama. Please make sure Ollama is running.")
        print("Run: ollama serve")
        sys.exit(1)

    # Check if llama3.2 model is available
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
            if response.status_code == 200:
                models = response.json()
                model_names = [model["name"] for model in models.get("models", [])]
                if not any("llama3.2" in name for name in model_names):
                    print("Warning: llama3.2 model not found. Pulling model...")
                    print("This may take a few minutes...")
                    pull_response = await client.post(
                        "http://localhost:11434/api/pull",
                        json={"name": "llama3.2"},
                        timeout=300.0
                    )
                    if pull_response.status_code != 200:
                        print("Error: Failed to pull llama3.2 model")
                        sys.exit(1)
    except Exception as e:
        print(f"Warning: Could not verify llama3.2 model availability: {e}")

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
