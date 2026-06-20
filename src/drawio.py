"""
🔌 Smart MCP - Wrapper MCP Drawio (persistent stdio transport)
Maintient un processus Node.js persistant pour garder la session drawio active
"""

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Optional


MCP_SERVER_PATH = os.getenv(
    "DRAWIO_MCP_PATH",
    "/home/malek/workspace/mcp-server-patched/dist/index.js"
)


class DrawioMCPError(Exception):
    pass


class DrawioMCPClient:
    """Client MCP Drawio avec processus Node.js persistant (stdio transport)"""

    def __init__(self, server_path: str = MCP_SERVER_PATH):
        self.server_path = server_path
        self._process: Optional[subprocess.Popen] = None
        self._initialized = False
        self._req_id = 1

    # ─── Gestion du processus persistant ───────────────────────────

    def _ensure_process(self):
        """Démarre le processus Node si pas déjà lancé"""
        if self._process is not None and self._process.poll() is None:
            return  # process already running

        self._process = subprocess.Popen(
            ["node", self.server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # line-buffered
        )
        self._initialized = False

    def _send_rpc(self, method: str, params: dict = None) -> dict:
        """Envoie un message JSON-RPC et attend la réponse (lecture ligne par ligne)"""
        self._ensure_process()

        req_id = self._req_id
        self._req_id += 1

        payload = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {},
        }

        # Écrire la requête sur stdin
        line = json.dumps(payload) + "\n"
        self._process.stdin.write(line)
        self._process.stdin.flush()

        # Lire les réponses jusqu'à trouver celle qui correspond à notre id
        while True:
            response_line = self._process.stdout.readline()
            if not response_line:
                # Process may have died
                stderr_output = self._process.stderr.read()
                raise DrawioMCPError(
                    f"MCP process died. stderr: {stderr_output[:300]}"
                )

            try:
                response = json.loads(response_line.strip())
            except json.JSONDecodeError:
                continue  # might be a log line, skip

            # Check for our response
            if response.get("id") == req_id:
                if "error" in response:
                    raise DrawioMCPError(
                        f"MCP error: {response['error']}"
                    )
                return response.get("result", {})
            elif response.get("id") is None and "method" in response:
                # This is a notification (like "initialized"), skip it
                continue

    def _rpc_call_tool(self, tool_name: str, arguments: dict = None) -> dict:
        """Appelle un outil MCP via tools/call, lève une erreur si isError"""
        result = self._send_rpc("tools/call", {
            "name": tool_name,
            "arguments": arguments or {},
        })
        # Vérifier si le tool a retourné une erreur
        if result.get("isError"):
            error_msg = "Unknown error"
            content = result.get("content", [])
            if content and len(content) > 0:
                error_msg = content[0].get("text", str(content))
            raise DrawioMCPError(error_msg)
        return result

    def _initialize(self):
        """Envoie la handshake initialize au serveur MCP"""
        if self._initialized:
            return

        self._ensure_process()

        # Step 1: initialize
        init_result = self._send_rpc("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "smart-mcp",
                "version": "1.0.0",
            },
        })

        # Step 2: send initialized notification (no response expected)
        notif = json.dumps({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }) + "\n"
        self._process.stdin.write(notif)
        self._process.stdin.flush()

        self._initialized = True
        time.sleep(0.5)  # Let the server settle

    # ─── API publique ──────────────────────────────────────────────

    def start_session(self) -> bool:
        """Démarre une session drawio (ouvre le browser)"""
        self._initialize()
        try:
            self._rpc_call_tool("start_session")
            return True
        except DrawioMCPError as e:
            print(f"⚠️ start_session: {e}")
            return False

    def get_diagram(self) -> Optional[str]:
        """Récupère le XML du diagramme courant"""
        try:
            result = self._rpc_call_tool("get_diagram")
            content = result.get("content", [])
            if content and len(content) > 0:
                return content[0].get("text", "")
            return None
        except DrawioMCPError:
            return None

    def list_pages(self) -> list[dict]:
        """Liste les pages du diagramme"""
        try:
            result = self._rpc_call_tool("list_pages")
            content = result.get("content", [{}])
            if content and len(content) > 0:
                text = content[0].get("text", "[]")
                # Parse format: "Pages (N):\n  [0] id=\"...\" name=\"...\" cells=N"
                pages = []
                for line in text.split("\n"):
                    line = line.strip()
                    if line.startswith("[") and "id=" in line:
                        import re
                        m = re.match(
                            r'\[(\d+)\]\s+id="([^"]*)"\s+name="([^"]*)"\s+cells=(\d+)',
                            line
                        )
                        if m:
                            pages.append({
                                "index": int(m.group(1)),
                                "id": m.group(2),
                                "name": m.group(3),
                                "cells": int(m.group(4)),
                            })
                return pages
            return []
        except DrawioMCPError:
            return []

    def create_new_diagram(self, xml: str) -> bool:
        """Crée un nouveau diagramme depuis du XML"""
        try:
            self._rpc_call_tool("create_new_diagram", {"xml": xml})
            return True
        except DrawioMCPError as e:
            print(f"⚠️ create_new_diagram: {e}")
            return False

    def edit_diagram(self, page_name: str, operations: list[dict]) -> bool:
        """Modifie le diagramme"""
        try:
            result = self._rpc_call_tool("edit_diagram", {
                "page_name": page_name,
                "operations": operations,
            })
            return result.get("content", [{}])[0].get("text", "") != ""
        except DrawioMCPError:
            return False

    def add_page(self, name: str, xml: str = "") -> Optional[str]:
        """Ajoute une page au diagramme"""
        try:
            args = {"name": name}
            if xml:
                args["xml"] = xml
            result = self._rpc_call_tool("add_page", args)
            return result.get("page_id")
        except DrawioMCPError as e:
            print(f"⚠️ add_page: {e}")
            return None

    def export_diagram(self, path: str, format: str = "drawio", page_name: str = "") -> bool:
        """Exporte le diagramme"""
        try:
            args = {"path": path, "format": format}
            if page_name:
                args["page_name"] = page_name
            self._rpc_call_tool("export_diagram", args)
            return Path(path).exists()
        except DrawioMCPError:
            return False

    @property
    def session_active(self) -> bool:
        """Indique si une session drawio est active"""
        return self._process is not None and self._process.poll() is None and self._initialized

    def close(self):
        """Ferme le processus proprement"""
        if self._process and self._process.poll() is None:
            self._process.stdin.close()
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None
            self._initialized = False


# Singleton
_client: Optional[DrawioMCPClient] = None


def get_drawio() -> DrawioMCPClient:
    global _client
    if _client is None:
        _client = DrawioMCPClient()
    return _client