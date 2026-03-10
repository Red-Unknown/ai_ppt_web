from typing import AsyncGenerator, Dict, Any, Optional
import asyncio
import uuid
import logging
import ast
from backend.app.utils.sandbox import SafeCodeExecutor, ExecutionError, SecurityError

logger = logging.getLogger(__name__)

class StreamingMathExecutor:
    """
    Handles streaming execution of Python code chunks.
    Maintains a session for stateful execution.
    """
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.code_buffer = ""
        
    def _is_executable(self, code: str) -> bool:
        """Check if the code block is syntactically complete."""
        if not code.strip():
            return False
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    async def stream_execute(self, code_stream: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
        """
        Consumes a stream of code chunks (tokens or lines), 
        accumulates them, and executes complete statements immediately.
        Yields execution results.
        """
        async for chunk in code_stream:
            self.code_buffer += chunk
            
            # Check if we have potential complete statements (e.g., ends with newline)
            if "\n" in chunk: 
                # Attempt to split buffer into statements and execute complete ones
                lines = self.code_buffer.split('\n')
                
                # Keep the last incomplete line in buffer
                # If buffer ends with \n, the last element is empty string
                if self.code_buffer.endswith('\n'):
                    pending_lines = []
                else:
                    pending_lines = [lines.pop()]
                
                # Try to form complete blocks from lines
                processed_lines = []
                current_block_lines = []
                
                # We need to iterate carefully. 
                # If we have lines ["a=1", "b=2"], "a=1" is executable.
                # If we have ["def foo():", "  pass"], "def foo():" is NOT executable.
                
                i = 0
                while i < len(lines):
                    line = lines[i]
                    current_block_lines.append(line)
                    candidate_code = "\n".join(current_block_lines)
                    
                    # Simplified block detection:
                    # If we can parse it, we execute it?
                    # Problem: "a = 1" parses. "a = 1\n" parses. "a = 1\nb=2" parses.
                    # If we execute "a=1", then buffer is empty. Next we see "b=2".
                    # This works for sequential statements.
                    # But for "def foo():", it fails parsing until we see "  pass".
                    
                    try:
                        ast.parse(candidate_code)
                        # It parses! But is it complete?
                        # If it ends with a colon, it's definitely not complete (but ast.parse might fail or succeed depending on version/context)
                        # Usually "def foo():" raises SyntaxError: unexpected EOF while parsing
                        
                        # So if it parses, it's likely a complete statement or block.
                        # Execute it!
                        
                        result = await self._execute_safe(candidate_code)
                        if result and result != "None":
                            yield result
                        # Reset block
                        current_block_lines = []
                        
                    except SyntaxError:
                        # Not complete yet
                        pass
                    i += 1
                
                # Reconstruct buffer with unexecuted lines
                self.code_buffer = "\n".join(current_block_lines + pending_lines)

        # At the end, execute whatever is left
        if self.code_buffer.strip():
             try:
                 result = await self._execute_safe(self.code_buffer)
                 if result and result != "None":
                     yield result
             except Exception as e:
                 yield f"Error: {str(e)}"

    async def _execute_safe(self, code: str) -> str:
        """Run code in the sandbox with the current session."""
        loop = asyncio.get_event_loop()
        try:
            # Run blocking execute in thread pool
            result = await loop.run_in_executor(
                None, 
                lambda: SafeCodeExecutor.execute(code, session_id=self.session_id)
            )
            return result
        except (ExecutionError, SecurityError) as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"System Error: {str(e)}"
