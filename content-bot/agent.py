"""
Content Bot AI Agent
Conversational AI powered by Claude with tool calling
"""

import os
import json
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

from tools import TOOLS, execute_tool

load_dotenv()


class ContentAgent:
    """Conversational AI agent powered by Claude"""

    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")

        self.client = Anthropic(api_key=api_key)
        self.conversation_history = []
        self.model = "claude-sonnet-4-20250514"

        self.system_prompt = """You are the AI agent for dopamine.watch content automation system.

You help manage a blog and content empire focused on ADHD and neurodivergent content. You can:
- Generate and publish blog posts
- Create SEO landing pages
- Check analytics and traffic
- Monitor site health
- Manage the posting schedule
- View recent posts and performance
- Run SEO audits
- Generate topic ideas

PERSONALITY:
- Be helpful, concise, and proactive
- Use emojis to make responses friendly but not excessive
- When asked to do something, use your tools to actually do it
- Always confirm actions were completed successfully
- Provide specific numbers and URLs when relevant
- Be enthusiastic about content wins and growth

CURRENT STATS:
- Blog: https://dopamine.watch/blog/
- App: https://app.dopamine.watch/
- Schedule: Monday & Thursday at 9 AM

When the user asks about the system, provide real data from tools.
When they ask you to do something, execute it and report the results."""

    def chat(self, user_message: str) -> str:
        """Send message and get response"""

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        try:
            # Call Claude with tools
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                messages=self.conversation_history,
                tools=TOOLS
            )

            # Handle tool calls in a loop
            while response.stop_reason == "tool_use":
                # Extract tool calls
                tool_use_blocks = [block for block in response.content if block.type == "tool_use"]

                # Execute each tool
                tool_results = []
                for tool_block in tool_use_blocks:
                    print(f"  ⚙️ Executing: {tool_block.name}...")
                    result = execute_tool(tool_block.name, tool_block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_block.id,
                        "content": json.dumps(result)
                    })

                # Add assistant response with tool use to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Add tool results to history
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })

                # Get next response
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=self.system_prompt,
                    messages=self.conversation_history,
                    tools=TOOLS
                )

            # Extract final text response
            text_response = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text_response += block.text

            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })

            return text_response

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            return error_msg

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def get_history(self) -> list:
        """Get conversation history"""
        history = []
        for msg in self.conversation_history:
            if msg["role"] == "user":
                content = msg["content"]
                if isinstance(content, str):
                    history.append({"role": "user", "content": content})
            elif msg["role"] == "assistant":
                content = msg["content"]
                if isinstance(content, list):
                    text = ""
                    for block in content:
                        if hasattr(block, "text"):
                            text += block.text
                    if text:
                        history.append({"role": "assistant", "content": text})
                elif isinstance(content, str):
                    history.append({"role": "assistant", "content": content})
        return history

    def save_conversation(self, filename: str = None):
        """Save conversation to file"""
        if not filename:
            filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        log_dir = os.path.join(os.path.dirname(__file__), "logs", "conversations")
        os.makedirs(log_dir, exist_ok=True)

        filepath = os.path.join(log_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(self.get_history(), f, indent=2)

        return filepath


# Quick test
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 Content Bot Agent Test")
    print("="*60 + "\n")

    try:
        agent = ContentAgent()
        print("✅ Agent initialized successfully!\n")

        # Test a simple query
        response = agent.chat("What's my current system status?")
        print(f"Response: {response}\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure ANTHROPIC_API_KEY is set in your .env file")
