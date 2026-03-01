import json
import logging
import time
from typing import List, Dict, Any, AsyncGenerator, Optional

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from backend.app.services.qa.tools.base import BaseSkill

logger = logging.getLogger(__name__)

class ReActAgent:
    """
    ReAct Agent that orchestrates the Thinking -> Acting -> Observing loop.
    Supports OpenAI Function Calling (Tools).
    """

    def __init__(
        self, 
        llm: ChatOpenAI, 
        tools: List[BaseSkill],
        max_iterations: int = 8,
        system_prompt: str = None
    ):
        self.llm = llm
        # Store tools by name for easy lookup
        self.tools = {tool.name: tool for tool in tools}
        self.max_iterations = max_iterations
        
        # Convert skills to OpenAI tool schemas
        self.tool_schemas = [tool.to_tool_schema() for tool in tools]
        
        # Bind tools to LLM
        # This tells the LLM which tools are available
        self.llm_with_tools = self.llm.bind_tools(self.tool_schemas)
        
        self.system_prompt = system_prompt or (
            "You are a helpful AI assistant capable of multi-step reasoning. "
            "Use the available tools to answer the user's question. "
            "Always think step-by-step before calling a tool. "
            "If you have enough information, provide the Final Answer."
        )

    async def run(
        self, 
        query: str, 
        history: List[Dict[str, str]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Run the ReAct loop and stream events.
        Yields JSON strings for SSE.
        """
        
        # 1. Initialize Messages
        messages: List[BaseMessage] = [SystemMessage(content=self.system_prompt)]
        
        # Add History
        if history:
            for msg in history:
                role = msg.get("role")
                content = msg.get("content")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
        
        # Add Current Query
        messages.append(HumanMessage(content=query))
        
        iteration = 0
        final_answer_reached = False

        try:
            while iteration < self.max_iterations and not final_answer_reached:
                iteration += 1
                logger.info(f"ReAct Loop Iteration {iteration}")
                yield json.dumps({"type": "iteration", "iteration": iteration})
                
                # Call LLM
                # Using ainvoke for simplicity and robustness in tool calling
                # Streaming tool calls is complex, so we stream the 'thought' after generation 
                # or if we switch to astream later.
                start_llm_time = time.time()
                response_msg = await self.llm_with_tools.ainvoke(messages)
                llm_duration = time.time() - start_llm_time
                
                # Log Cache Usage if available (DeepSeek)
                usage_metadata = {}
                if hasattr(response_msg, "response_metadata"):
                    usage_metadata = response_msg.response_metadata.get("usage", {})
                elif hasattr(response_msg, "additional_kwargs"):
                    # Fallback for older LangChain versions or different providers
                    usage_metadata = response_msg.additional_kwargs.get("usage", {})
                
                if usage_metadata:
                    cache_hit = usage_metadata.get("prompt_cache_hit_tokens", 0)
                    cache_miss = usage_metadata.get("prompt_cache_miss_tokens", 0)
                    total_tokens = usage_metadata.get("total_tokens", 0)
                    logger.info(f"LLM Usage - Hit: {cache_hit}, Miss: {cache_miss}, Total: {total_tokens}")
                    yield json.dumps({
                        "type": "usage", 
                        "hit_tokens": cache_hit, 
                        "miss_tokens": cache_miss,
                        "total_tokens": total_tokens
                    })

                # Append the assistant's response to history
                messages.append(response_msg)
                
                # Safe tool call extraction
                tool_calls = getattr(response_msg, "tool_calls", [])
                if not tool_calls and hasattr(response_msg, "additional_kwargs"):
                    raw_tool_calls = response_msg.additional_kwargs.get("tool_calls", [])
                    if raw_tool_calls:
                        # Normalize OpenAI format to LangChain tool_call dict format
                        tool_calls = []
                        for tc in raw_tool_calls:
                            function_data = tc.get("function", {})
                            tool_calls.append({
                                "name": function_data.get("name"),
                                "args": json.loads(function_data.get("arguments", "{}")),
                                "id": tc.get("id")
                            })

                # Check for tool calls
                if tool_calls:
                    # If there is content (Thought), yield it
                    if response_msg.content:
                        yield json.dumps({"type": "thought", "content": response_msg.content})
                    
                    # Execute Tools
                    for tool_call in tool_calls:
                        func_name = tool_call["name"]
                        args = tool_call["args"]
                        call_id = tool_call["id"]
                        
                        # MCP: tool_start
                        yield json.dumps({
                            "type": "tool_start", 
                            "tool_call_id": call_id,
                            "tool_name": func_name,
                            "inputs": args,
                            "description": f"Calling {func_name}...",
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                        
                        tool_instance = self.tools.get(func_name)
                        output_content = ""
                        status = "error"
                        render_type = "text"
                        error_trace = None
                        
                        if tool_instance:
                            try:
                                start_time = time.time()
                                # Execute tool
                                tool_result = await tool_instance.execute(**args)
                                duration = time.time() - start_time
                                
                                output_content = str(tool_result.get("content", ""))
                                status = tool_result.get("status", "success")
                                render_type = tool_result.get("render_type", "text")
                                
                                # Log Structured Tool Execution
                                logger.info(json.dumps({
                                    "event": "tool_execution",
                                    "tool": func_name,
                                    "inputs": args,
                                    "outputs": output_content[:200] + "..." if len(output_content) > 200 else output_content,
                                    "duration": duration,
                                    "status": status,
                                    "timestamp": time.time()
                                }, ensure_ascii=False))

                                # MCP: tool_result
                                yield json.dumps({
                                    "type": "tool_result",
                                    "tool_call_id": call_id,
                                    "tool_name": func_name,
                                    "status": status,
                                    "output": output_content,
                                    "render_type": render_type,
                                    "execution_time": duration,
                                    "inputs": args # Echo inputs for frontend detail view
                                })
                                
                            except Exception as e:
                                import traceback
                                error_trace = traceback.format_exc()
                                output_content = f"Error executing tool {func_name}: {str(e)}"
                                logger.error(f"Tool Error: {output_content}\n{error_trace}")
                                
                                # MCP: tool_error
                                yield json.dumps({
                                    "type": "tool_error", 
                                    "tool_call_id": call_id,
                                    "tool_name": func_name,
                                    "status": "error",
                                    "error_message": str(e),
                                    "error_details": error_trace,
                                    "inputs": args
                                })
                        else:
                            output_content = f"Error: Tool '{func_name}' not found."
                            logger.error(output_content)
                            # MCP: tool_error
                            yield json.dumps({
                                "type": "tool_error", 
                                "tool_call_id": call_id,
                                "tool_name": func_name,
                                "status": "error",
                                "error_message": f"Tool '{func_name}' not found",
                                "error_details": "Tool not registered in agent",
                                "inputs": args
                            })

                        # Append Tool Output to History
                        messages.append(ToolMessage(
                            content=output_content,
                            tool_call_id=call_id,
                            name=func_name,
                            status=status
                        ))
                        
                else:
                    # No tool calls -> Final Answer
                    final_answer_reached = True
                    # Yield the final answer
                    # Note: If content is empty, it's an issue, but usually it's not.
                    if response_msg.content:
                        yield json.dumps({"type": "answer", "content": response_msg.content})
                    else:
                        yield json.dumps({"type": "answer", "content": "I'm not sure how to answer that."})
            
            if iteration >= self.max_iterations and not final_answer_reached:
                yield json.dumps({"type": "error", "content": "Max iterations reached without a final answer."})
                
        except Exception as e:
            logger.error(f"ReAct Agent Error: {e}", exc_info=True)
            yield json.dumps({"type": "error", "content": f"System Error: {str(e)}"})
        
        # Done signal
        yield json.dumps({"type": "done"})
