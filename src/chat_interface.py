import requests
import json
import os
import sys
from datetime import datetime

class ChatInterface:
    def __init__(self, api_url, log_file="conversation_log.json"):
        self.api_url = api_url.rstrip("/")
        self.log_file = log_file
        self.session_history = []
        self.load_log()

    def load_log(self):
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    self.session_history = json.load(f)
            except Exception:
                self.session_history = []

    def save_log(self):
        with open(self.log_file, "w") as f:
            json.dump(self.session_history, f, indent=2)

    def log_conversation(self, query, mode, result):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "mode": mode,
            "response": result.get("answer", ""),
            "sources": result.get("sources", [])
        }
        self.session_history.append(entry)
        self.save_log()

    def send_request(self, query, mode="rag", top_k=3, prompt_key="base_retrieval_prompt"):
        try:
            if mode == "rag":
                endpoint = f"{self.api_url}/chat"
                payload = {"question": query, "k": top_k, "prompt_key": prompt_key}
            else:
                endpoint = f"{self.api_url}/ping"
                payload = {"prompt": query}

            resp = requests.post(endpoint, json=payload, timeout=30)
            if resp.status_code == 200:
                result = resp.json()
                self.log_conversation(query, mode, result)
                return result
            else:
                return {"answer": f"Error: {resp.status_code} - {resp.text}"}
        except Exception as e:
            return {"answer": f"Exception: {str(e)}"}

    def display_response(self, result):
        print("\n--- Shoplite Assistant ---\n")
        print(result.get("answer", "No response received"))

        if "sources" in result and result["sources"]:
            print("\n" + "-"*60)
            print("SOURCES:")
            for i, doc in enumerate(result["sources"], 1):
                print(f"  {i}. {doc}")

    def health_check(self):
        try:
            resp = requests.get(f"{self.api_url}/health")
            if resp.status_code == 200:
                data = resp.json()
                print("API Health Check: ✅")
                print(f"✓ Status: {data.get('status')}")
                print(f"✓ Model: {data.get('model')}")
                print(f"✓ Knowledge base: {data.get('docs', 0)} documents\n")
            else:
                print(f"API Health Check Failed: {resp.status_code}")
        except Exception as e:
            print(f"Health check error: {str(e)}")

    def run(self):
        print("="*60)
        print("Shoplite Assistant Chat Interface")
        print("Type '/help' for commands. Type '/quit' to exit.")
        print("="*60)

        self.health_check()

        mode = "rag"
        prompt_key = "base_retrieval_prompt"

        while True:
            query = input("\nYou: ").strip()
            if not query:
                continue

            if query.lower() == "/quit":
                print("Goodbye!")
                break
            elif query.lower() == "/help":
                print("\nCommands:")
                print("  /quit      Exit the chat")
                print("  /mode      Switch between rag and direct LLM modes")
                print("  /save      Save conversation log")
                print("  /clear     Clear conversation log")
                print("  /prompt    Switch prompt type")
                continue
            elif query.lower() == "/mode":
                mode = "direct" if mode == "rag" else "rag"
                print(f"Switched mode to: {mode}")
                continue
            elif query.lower() == "/save":
                self.save_log()
                print(f"Conversation saved to {self.log_file}")
                continue
            elif query.lower() == "/clear":
                self.session_history = []
                self.save_log()
                print("Conversation log cleared")
                continue
            elif query.lower() == "/prompt":
                print("Available prompts:", list(PROMPTS.keys()))
                new_key = input("Enter prompt key: ").strip()
                if new_key in PROMPTS:
                    prompt_key = new_key
                    print(f"Prompt switched to: {prompt_key}")
                else:
                    print("Invalid prompt key")
                continue

            result = self.send_request(query, mode=mode, prompt_key=prompt_key)
            self.display_response(result)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python chat-interface.py <API_URL>")
        sys.exit(1)

    api_url = sys.argv[1]
    interface = ChatInterface(api_url)
    interface.run()
