#!/usr/bin/env python3
"""
Channel Dispatcher - Invia messaggi proattivi su Telegram e WhatsApp
Integrazione con i provider di messaggistica di OpenClaw
"""

import os
import subprocess
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger('emotion_engine')


class ChannelDispatcher:
    """
    Dispatcher per inviare messaggi proattivi su diversi canali.
    
    Supporta:
    - Telegram (via openclaw CLI)
    - WhatsApp (via openclaw CLI)
    
    In futuro potrà supportare anche Slack, Email, etc.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.default_channel = self.config.get("default_channel", "telegram")
        
        # Configurazione canali
        self.channels = {
            "telegram": {
                "enabled": True,
                "provider": "telegram",
                "command": "openclaw message send --channel telegram --text",
                "emoji_support": True,
                "max_length": 4096,
                "target": self.config.get("telegram_target", "")  # chat_id
            },
            "whatsapp": {
                "enabled": True,
                "provider": "whatsapp", 
                "command": "openclaw message send --channel whatsapp --text",
                "emoji_support": True,
                "max_length": 1600,
                "target": self.config.get("whatsapp_target", "")  # phone number
            }
        }
    
    def send_message(self, message: str, channel: str = None, **kwargs) -> Dict[str, Any]:
        """
        Invia un messaggio sul canale specificato.
        
        Args:
            message: Testo del messaggio
            channel: Canale target (telegram/whatsapp)
            **kwargs: Parametri aggiuntivi
            
        Returns:
            Dict con risultato dell'invio
        """
        channel = channel or self.default_channel
        
        if channel not in self.channels:
            return {
                "success": False,
                "error": f"Canale non supportato: {channel}",
                "supported_channels": list(self.channels.keys())
            }
        
        channel_config = self.channels[channel]
        
        if not channel_config["enabled"]:
            return {
                "success": False,
                "error": f"Canale {channel} disabilitato"
            }
        
        # Tronca messaggio se troppo lungo
        max_length = channel_config.get("max_length", 4000)
        if len(message) > max_length:
            message = message[:max_length-3] + "..."
            logger.warning(f"Messaggio troncato per {channel}")
        
        # Invia messaggio
        try:
            if channel == "telegram":
                return self._send_telegram(message, **kwargs)
            elif channel == "whatsapp":
                return self._send_whatsapp(message, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Implementazione mancante per canale: {channel}"
                }
        
        except Exception as e:
            logger.error(f"Errore invio messaggio su {channel}: {e}")
            return {
                "success": False,
                "error": str(e),
                "channel": channel
            }
    
    def _check_openclaw_config(self, channel: str) -> tuple[bool, str]:
        """Verifica che OpenClaw sia configurato per un canale."""
        try:
            # Prova a listare i canali configurati
            result = subprocess.run(
                'openclaw channels list --json 2>/dev/null || echo "[]"',
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return False, "OpenClaw CLI non disponibile o non configurato"
            
            # Verifica se il canale è nella lista
            if channel.lower() not in result.stdout.lower():
                return False, f"Canale {channel} non configurato in OpenClaw. Usa: openclaw channels add --channel {channel}"
            
            return True, "OK"
        except Exception as e:
            return False, f"Errore verifica configurazione: {e}"
    
    def _send_telegram(self, message: str, **kwargs) -> Dict[str, Any]:
        """Invia messaggio su Telegram via openclaw CLI."""
        try:
            # Ottieni target (chat_id)
            target = kwargs.get('target') or self.channels["telegram"].get("target", "")
            if not target:
                return {
                    "success": False,
                    "channel": "telegram",
                    "error": "Target (chat_id) non configurato. Usa: /emotions proactive target <chat_id>"
                }
            
            # Verifica configurazione OpenClaw
            logger.info("Verifica configurazione OpenClaw per WhatsApp...")
            config_ok, config_error = self._check_openclaw_config("whatsapp")
            if not config_ok:
                logger.error(f"Configurazione OpenClaw mancante: {config_error}")
                return {
                    "success": False,
                    "channel": "whatsapp",
                    "error": f"Configurazione OpenClaw mancante: {config_error}. Configura prima il canale WhatsApp in OpenClaw."
                }
            logger.info("Configurazione OpenClaw OK")
            logger.info("Configurazione OpenClaw OK")
            
            # Prova a usare openclaw CLI
            # Formatta il messaggio per la shell
            escaped_message = message.replace('"', '\\"')
            
            # Comando per inviare messaggio con target
            cmd = f'openclaw message send --channel telegram --target "{target}" --message "{escaped_message}"'
            
            logger.info(f"Invio messaggio Telegram: {message[:50]}...")
            
            # Esegui comando
            logger.info(f"Esecuzione comando: {cmd[:100]}...")
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Log output per debugging
            if result.stdout:
                logger.info(f"Command stdout: {result.stdout}")
            if result.stderr:
                logger.warning(f"Command stderr: {result.stderr}")
            
            if result.returncode == 0:
                logger.info("Messaggio Telegram inviato con successo")
                return {
                    "success": True,
                    "channel": "telegram",
                    "message_preview": message[:100],
                    "output": result.stdout
                }
            else:
                error_msg = result.stderr or result.stdout or "Errore sconosciuto"
                logger.error(f"Errore invio Telegram (exit code {result.returncode}): {error_msg}")
                # Fallback: stampa il messaggio che sarebbe stato inviato
                print(f"\n{'='*60}")
                print("📨 MESSAGGIO PROATTIVO (fallback - non inviato)")
                print(f"{'='*60}")
                print(f"Canale: Telegram")
                print(f"Target: {target}")
                print(f"{'='*60}")
                print(message)
                print(f"{'='*60}\n")
                return {
                    "success": False,
                    "channel": "telegram",
                    "error": error_msg,
                    "exit_code": result.returncode,
                    "fallback_shown": True
                }
        
        except subprocess.TimeoutExpired:
            logger.error("Timeout invio messaggio Telegram")
            return {
                "success": False,
                "channel": "telegram",
                "error": "Timeout durante l'invio"
            }
        except Exception as e:
            logger.error(f"Errore invio Telegram: {e}")
            return {
                "success": False,
                "channel": "telegram",
                "error": str(e)
            }
    
    def _send_whatsapp(self, message: str, **kwargs) -> Dict[str, Any]:
        """Invia messaggio su WhatsApp via openclaw CLI."""
        try:
            # Ottieni target (phone number)
            target = kwargs.get('target') or self.channels["whatsapp"].get("target", "")
            if not target:
                return {
                    "success": False,
                    "channel": "whatsapp",
                    "error": "Target (phone number) non configurato. Usa: /emotions proactive target <phone>"
                }
            
            # Formatta il messaggio per la shell
            escaped_message = message.replace('"', '\\"')
            
            # Comando per inviare messaggio con target
            cmd = f'openclaw message send --channel whatsapp --target "{target}" --message "{escaped_message}"'
            
            logger.info(f"Invio messaggio WhatsApp: {message[:50]}...")
            
            # Esegui comando
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("Messaggio WhatsApp inviato con successo")
                return {
                    "success": True,
                    "channel": "whatsapp",
                    "message_preview": message[:100]
                }
            else:
                error_msg = result.stderr or "Errore sconosciuto"
                logger.error(f"Errore invio WhatsApp: {error_msg}")
                return {
                    "success": False,
                    "channel": "whatsapp",
                    "error": error_msg
                }
        
        except subprocess.TimeoutExpired:
            logger.error("Timeout invio messaggio WhatsApp")
            return {
                "success": False,
                "channel": "whatsapp",
                "error": "Timeout durante l'invio"
            }
        except Exception as e:
            logger.error(f"Errore invio WhatsApp: {e}")
            return {
                "success": False,
                "channel": "whatsapp",
                "error": str(e)
            }
    
    def test_channel(self, channel: str = None) -> Dict[str, Any]:
        """
        Testa la connessione con un canale.
        
        Args:
            channel: Canale da testare (default: telegram)
            
        Returns:
            Dict con risultato del test
        """
        channel = channel or self.default_channel
        
        test_message = "🧪 Test di connessione - Emotion Engine Proactive System"
        
        result = self.send_message(test_message, channel)
        
        if result.get("success"):
            return {
                "success": True,
                "channel": channel,
                "message": f"Canale {channel} funzionante",
                "test_sent": True
            }
        else:
            return {
                "success": False,
                "channel": channel,
                "message": f"Problema con canale {channel}",
                "error": result.get("error", "Errore sconosciuto"),
                "test_sent": False
            }
    
    def get_available_channels(self) -> Dict[str, Dict[str, Any]]:
        """Restituisce lista canali disponibili."""
        return {
            name: {
                "enabled": config["enabled"],
                "emoji_support": config["emoji_support"],
                "max_length": config["max_length"]
            }
            for name, config in self.channels.items()
        }
    
    def set_default_channel(self, channel: str) -> bool:
        """Imposta canale predefinito."""
        if channel not in self.channels:
            return False
        
        self.default_channel = channel
        self.config["default_channel"] = channel
        logger.info(f"Canale predefinito cambiato a: {channel}")
        return True


class MockChannelDispatcher(ChannelDispatcher):
    """
    Versione mock del dispatcher per testing senza inviare messaggi reali.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.sent_messages = []
    
    def send_message(self, message: str, channel: str = None, **kwargs) -> Dict[str, Any]:
        """Simula invio messaggio senza inviarlo realmente."""
        channel = channel or self.default_channel
        
        # Registra messaggio
        self.sent_messages.append({
            "channel": channel,
            "message": message,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
        
        logger.info(f"[MOCK] Messaggio inviato su {channel}: {message[:50]}...")
        
        return {
            "success": True,
            "channel": channel,
            "message_preview": message[:100],
            "mock": True
        }
    
    def get_sent_messages(self) -> list:
        """Restituisce lista messaggi inviati (solo per testing)."""
        return self.sent_messages
    
    def clear_sent_messages(self):
        """Pulisci lista messaggi inviati."""
        self.sent_messages = []
