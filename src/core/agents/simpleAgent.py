# src/core/simple_agent.py
import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class SimpleAgent:
    def __init__(self, name: str, prompt: str, mcp_client=None):
        self.name = name
        self.prompt = prompt
        self.mcp_client = mcp_client
        self.client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            timeout=float(os.getenv("LLM_TIMEOUT", 60)),
        )
        self.model = os.getenv("LLM_MODEL_ID", "deepseek-chat")

    def run(self, user_message: str) -> str:
        # 第一次调用 LLM
        messages = [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": user_message},
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        llm_reply = response.choices[0].message.content

        # 检查是否有工具调用
        tool_call = self._parse_tool_call(llm_reply)
        if tool_call and self.mcp_client:
            # 执行工具
            tool_result = self.mcp_client.call_tool(
                tool_name=tool_call["tool"],
                arguments=tool_call["params"],
            )

            # 把工具结果加入对话，让 LLM 总结
            messages.append({"role": "assistant", "content": llm_reply})
            messages.append(
                {
                    "role": "user",
                    "content": f"工具返回结果：\n{tool_result}\n\n请根据以上结果回答用户。",
                }
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return response.choices[0].message.content

        return llm_reply

    def _parse_tool_call(self, text: str) -> dict | None:
        pattern = r"\[TOOL_CALL:(\w+):(.*?)\]"
        match = re.search(pattern, text)
        if not match:
            return None
        tool_name = match.group(1)
        params = dict(p.split("=") for p in match.group(2).split(","))
        return {"tool": tool_name, "params": params}

    def __repr__(self):
        return f"SimpleAgent(name={self.name!r}, model={self.model!r})"
