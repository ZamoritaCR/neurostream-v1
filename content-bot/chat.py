#!/usr/bin/env python3
"""
Content Bot Chat Interface
Beautiful terminal-based chat with the AI agent
"""

import os
import sys
from datetime import datetime

# Try to import rich for beautiful formatting
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich.text import Text
    from rich.live import Live
    from rich.spinner import Spinner
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from dotenv import load_dotenv
load_dotenv()

from agent import ContentAgent


class ChatInterface:
    """Terminal chat interface for Content Bot"""

    def __init__(self):
        self.agent = None
        self.running = True

        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None

    def print_header(self):
        """Print welcome header"""
        if RICH_AVAILABLE:
            header = """
[bold cyan]🤖 Content Bot Agent[/bold cyan]
[dim]Your AI-powered content automation assistant[/dim]

[bold green]Commands:[/bold green]
  [cyan]help[/cyan]     - Show available commands
  [cyan]status[/cyan]   - Check system status
  [cyan]clear[/cyan]    - Clear conversation
  [cyan]save[/cyan]     - Save conversation
  [cyan]exit[/cyan]     - Exit chat

[dim]Just type naturally to interact with your content empire![/dim]
"""
            self.console.print(Panel(header, title="[bold white]dopamine.watch[/bold white]", border_style="cyan"))
        else:
            print("\n" + "="*60)
            print("🤖 Content Bot Agent")
            print("Your AI-powered content automation assistant")
            print("="*60)
            print("\nCommands: help, status, clear, save, exit")
            print("Just type naturally to interact!\n")

    def print_message(self, role: str, content: str):
        """Print a chat message"""
        if RICH_AVAILABLE:
            if role == "user":
                self.console.print(f"\n[bold blue]You:[/bold blue] {content}")
            elif role == "assistant":
                self.console.print(f"\n[bold green]Agent:[/bold green]")
                # Try to render as markdown
                try:
                    self.console.print(Markdown(content))
                except:
                    self.console.print(content)
            elif role == "system":
                self.console.print(f"\n[dim]{content}[/dim]")
            elif role == "error":
                self.console.print(f"\n[bold red]Error:[/bold red] {content}")
        else:
            if role == "user":
                print(f"\nYou: {content}")
            elif role == "assistant":
                print(f"\nAgent: {content}")
            elif role == "system":
                print(f"\n[{content}]")
            elif role == "error":
                print(f"\nError: {content}")

    def get_input(self) -> str:
        """Get user input"""
        if RICH_AVAILABLE:
            try:
                return Prompt.ask("\n[bold cyan]You[/bold cyan]")
            except (KeyboardInterrupt, EOFError):
                return "exit"
        else:
            try:
                return input("\nYou: ").strip()
            except (KeyboardInterrupt, EOFError):
                return "exit"

    def show_thinking(self):
        """Show thinking indicator"""
        if RICH_AVAILABLE:
            return Live(Spinner("dots", text="[dim]Thinking...[/dim]"), console=self.console, transient=True)
        return None

    def handle_command(self, user_input: str) -> bool:
        """Handle special commands. Returns True if handled."""
        cmd = user_input.lower().strip()

        if cmd == "exit" or cmd == "quit" or cmd == "bye":
            self.print_message("system", "Goodbye! Your content empire awaits. 🚀")
            self.running = False
            return True

        elif cmd == "clear":
            self.agent.clear_history()
            if RICH_AVAILABLE:
                self.console.clear()
            else:
                os.system('clear' if os.name == 'posix' else 'cls')
            self.print_header()
            self.print_message("system", "Conversation cleared!")
            return True

        elif cmd == "save":
            filepath = self.agent.save_conversation()
            self.print_message("system", f"Conversation saved to: {filepath}")
            return True

        elif cmd == "help":
            help_text = """
**Available Commands:**
- `help` - Show this help message
- `status` - Check system status
- `clear` - Clear conversation history
- `save` - Save conversation to file
- `exit` - Exit the chat

**Example Queries:**
- "Generate a post about ADHD sleep"
- "How's traffic doing?"
- "Check site health"
- "What posts do we have?"
- "Give me 5 topic ideas for productivity"
- "Create landing pages for anxiety"
- "Start the scheduler"
"""
            self.print_message("assistant", help_text)
            return True

        elif cmd == "status":
            # Quick status check
            response = self.agent.chat("Give me a quick status overview of all systems, posts, and analytics.")
            self.print_message("assistant", response)
            return True

        return False

    def run(self):
        """Main chat loop"""

        # Print header
        self.print_header()

        # Initialize agent
        self.print_message("system", "Initializing agent...")

        try:
            self.agent = ContentAgent()
            self.print_message("system", "Agent ready! How can I help?")
        except Exception as e:
            self.print_message("error", str(e))
            self.print_message("system", "Make sure ANTHROPIC_API_KEY is set in .env")
            return

        # Main loop
        while self.running:
            # Get input
            user_input = self.get_input()

            if not user_input:
                continue

            # Check for commands
            if self.handle_command(user_input):
                continue

            # Send to agent
            thinking = self.show_thinking()
            try:
                if thinking:
                    with thinking:
                        response = self.agent.chat(user_input)
                else:
                    print("  Thinking...")
                    response = self.agent.chat(user_input)

                self.print_message("assistant", response)

            except Exception as e:
                self.print_message("error", str(e))


def main():
    """Entry point"""
    chat = ChatInterface()
    chat.run()


if __name__ == "__main__":
    main()
