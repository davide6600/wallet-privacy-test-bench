"""
adapters/electrum.py
Adapter per l'automazione headless del client Electrum CLI e per scenari di simulazione protocol-compliant.
"""

from __future__ import annotations
import asyncio
import json
import logging
import os
import shutil
import socket
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ElectrumAdapter")


class ElectrumAdapter:
    def __init__(
        self,
        binary_path: str = "electrum",
        proxy_host: str = "127.0.0.1",
        proxy_port: int = 50001,
        test_dir: str = "artifacts/sandbox/electrum_data",
    ):
        self.binary_path = binary_path
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.test_dir = Path(test_dir)

    def is_binary_available(self) -> bool:
        return shutil.which(self.binary_path) is not None

    def clean_storage(self) -> None:
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def run_cli_command(self, args: List[str], timeout: int = 15) -> subprocess.CompletedProcess:
        cmd = [
            self.binary_path,
            "--regtest",
            "-D",
            str(self.test_dir),
            "-s",
            f"{self.proxy_host}:{self.proxy_port}:t",
            "--oneserver",
        ] + args
        logger.info(f"Esecuzione comando Electrum: {' '.join(cmd)}")
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

    async def execute_protocol_client_session_async(
        self,
        canary_scripthashes: List[str],
        do_broadcast: bool = True,
        raw_tx_hex: str = "02000000000101canarytestrawtx00000000",
    ) -> List[str]:
        """
        Esegue una sessione client conforme al protocollo Electrum direttamente via socket TCP asincrono
        verso il proxy osservatore.
        """
        reader, writer = await asyncio.open_connection(self.proxy_host, self.proxy_port)
        responses = []
        try:
            # 1. Handshake server.version
            req_ver = json.dumps({"id": 1, "method": "server.version", "params": ["Electrum-Client-Bench", ["1.4", "2.0"]]}) + "\n"
            writer.write(req_ver.encode("utf-8"))
            await writer.drain()
            resp = await reader.readline()
            responses.append(resp.decode("utf-8", errors="replace"))

            # 2. Sottoscrizione scripthash canary (simula restore & sync)
            req_id = 2
            for sh in canary_scripthashes:
                req_sub = json.dumps({"id": req_id, "method": "blockchain.scripthash.subscribe", "params": [sh]}) + "\n"
                writer.write(req_sub.encode("utf-8"))
                await writer.drain()
                resp = await reader.readline()
                responses.append(resp.decode("utf-8", errors="replace"))
                req_id += 1

                # Simula get_history
                req_hist = json.dumps({"id": req_id, "method": "blockchain.scripthash.get_history", "params": [sh]}) + "\n"
                writer.write(req_hist.encode("utf-8"))
                await writer.drain()
                resp = await reader.readline()
                responses.append(resp.decode("utf-8", errors="replace"))
                req_id += 1

            # 3. Trasmissione transazione (broadcast) nella stessa sessione se richiesto
            if do_broadcast:
                req_tx = json.dumps({"id": req_id, "method": "blockchain.transaction.broadcast", "params": [raw_tx_hex]}) + "\n"
                writer.write(req_tx.encode("utf-8"))
                await writer.drain()
                resp = await reader.readline()
                responses.append(resp.decode("utf-8", errors="replace"))
        finally:
            writer.close()
            await writer.wait_closed()

        return responses

    def execute_protocol_client_session(
        self,
        canary_scripthashes: List[str],
        do_broadcast: bool = True,
        raw_tx_hex: str = "02000000000101canarytestrawtx00000000",
    ) -> List[str]:
        return asyncio.run(
            self.execute_protocol_client_session_async(
                canary_scripthashes=canary_scripthashes,
                do_broadcast=do_broadcast,
                raw_tx_hex=raw_tx_hex,
            )
        )
