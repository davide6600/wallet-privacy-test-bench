"""
harness/observer_proxy.py
Proxy asincrono di intercettazione e logging per il protocollo Electrum JSON-RPC.
"""

from __future__ import annotations
import argparse
import asyncio
import datetime
import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ObserverProxy")


class ElectrumObserverProxy:
    def __init__(
        self,
        listen_host: str = "0.0.0.0",
        listen_port: int = 50001,
        backend_host: str = "127.0.0.1",
        backend_port: int = 60401,
        log_file: str = "artifacts/observed.jsonl",
        observer_id: str = "observer-electrum-rpc-50001",
    ):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.backend_host = backend_host
        self.backend_port = backend_port
        self.log_file = Path(log_file)
        self.observer_id = observer_id
        self._server: Optional[asyncio.Server] = None
        self._active_connections = 0

        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def _append_log(self, record: Dict[str, Any]) -> None:
        """Salva l'evento formattato in formato JSON Lines (append-only)."""
        line = json.dumps(record, ensure_ascii=False)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def _extract_scripthash(self, method: str, params: list) -> Optional[str]:
        if "scripthash" in method and params and isinstance(params[0], str):
            val = params[0].strip().lower()
            if len(val) == 64:
                return val
        return None

    async def _handle_client(
        self, client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter
    ) -> None:
        session_id = f"sess-{uuid.uuid4().hex[:8]}"
        peername = client_writer.get_extra_info("peername") or ("unknown", 0)
        client_ip, client_port = peername[0], peername[1]
        self._active_connections += 1

        logger.info(f"Nuova sessione [{session_id}] connessa da {client_ip}:{client_port}")

        # Tenta connessione al backend reale electrs
        backend_reader: Optional[asyncio.StreamReader] = None
        backend_writer: Optional[asyncio.StreamWriter] = None
        try:
            backend_reader, backend_writer = await asyncio.open_connection(
                self.backend_host, self.backend_port
            )
        except Exception as e:
            logger.warning(
                f"[{session_id}] Impossibile connettersi al backend {self.backend_host}:{self.backend_port} ({e}). Modalità fallback mockup attiva."
            )

        async def forward_backend_to_client():
            if not backend_reader:
                return
            try:
                while True:
                    data = await backend_reader.readline()
                    if not data:
                        break
                    client_writer.write(data)
                    await client_writer.drain()
            except Exception as ex:
                logger.debug(f"[{session_id}] Chiusura canale backend->client: {ex}")

        # Task di risposta da backend a client
        backend_task = asyncio.create_task(forward_backend_to_client())

        try:
            while True:
                line = await client_reader.readline()
                if not line:
                    break

                raw_line = line.decode("utf-8", errors="replace").strip()
                if not raw_line:
                    continue

                timestamp_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

                try:
                    payload = json.loads(raw_line)
                    method = payload.get("method", "unknown")
                    params = payload.get("params", [])
                    rpc_id = payload.get("id")
                    scripthash = self._extract_scripthash(method, params)

                    record = {
                        "timestamp_iso": timestamp_iso,
                        "observer_id": self.observer_id,
                        "protocol": "electrum-jsonrpc",
                        "session_id": session_id,
                        "client_ip": client_ip,
                        "client_port": client_port,
                        "direction": "request",
                        "rpc_id": rpc_id,
                        "method": method,
                        "params": params,
                        "scripthash": scripthash,
                        "raw_payload_size_bytes": len(line),
                    }
                    self._append_log(record)
                    logger.debug(f"[{session_id}] RPC: {method} scripthash={scripthash}")

                    # Se il backend è collegato, inoltra
                    if backend_writer:
                        backend_writer.write(line)
                        await backend_writer.drain()
                    else:
                        # Risposta di fallback per test isolati senza backend attivo
                        mock_resp = {
                            "jsonrpc": "2.0",
                            "id": rpc_id,
                            "result": [] if "get_history" in method else (None if "subscribe" in method else "mock-server"),
                        }
                        client_writer.write((json.dumps(mock_resp) + "\n").encode("utf-8"))
                        await client_writer.drain()

                except json.JSONDecodeError:
                    logger.warning(f"[{session_id}] Messaggio non-JSON ricevuto: {raw_line[:80]}")

        except Exception as e:
            logger.error(f"[{session_id}] Errore di connessione: {e}")
        finally:
            backend_task.cancel()
            if backend_writer:
                backend_writer.close()
            client_writer.close()
            await client_writer.wait_closed()
            self._active_connections -= 1
            logger.info(f"Sessione [{session_id}] terminata.")

    async def start(self) -> None:
        self._server = await asyncio.start_server(
            self._handle_client, self.listen_host, self.listen_port
        )
        addr = self._server.sockets[0].getsockname()
        logger.info(f"Observer Proxy in ascolto su {addr[0]}:{addr[1]} -> backend {self.backend_host}:{self.backend_port}")

    async def stop(self) -> None:
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            logger.info("Observer Proxy arrestato.")


def main():
    parser = argparse.ArgumentParser(description="Wallet Privacy Test Bench - Observer Proxy")
    parser.add_argument("--listen-host", default="0.0.0.0")
    parser.add_argument("--listen-port", type=int, default=int(os.getenv("LISTEN_PORT", "50001")))
    parser.add_argument("--backend-host", default=os.getenv("BACKEND_HOST", "127.0.0.1"))
    parser.add_argument("--backend-port", type=int, default=int(os.getenv("BACKEND_PORT", "60401")))
    parser.add_argument("--log-file", default=os.getenv("LOG_FILE", "artifacts/observed.jsonl"))

    args = parser.parse_args()

    proxy = ElectrumObserverProxy(
        listen_host=args.listen_host,
        listen_port=args.listen_port,
        backend_host=args.backend_host,
        backend_port=args.backend_port,
        log_file=args.log_file,
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(proxy.start())
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Interruzione manuale (SIGINT).")
    finally:
        loop.run_until_complete(proxy.stop())
        loop.close()


if __name__ == "__main__":
    main()
