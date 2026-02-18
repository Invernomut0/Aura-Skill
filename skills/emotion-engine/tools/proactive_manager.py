#!/usr/bin/env python3
"""
Proactive Emotion Engine - Gestisce comportamento proattivo basato sulle emozioni
L'agente può iniziare conversazioni spontanee quando emozioni specifiche superano le soglie
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger('emotion_engine')


class ProactiveTriggerManager:
    """
    Gestisce il comportamento proattivo dell'agente basato sulle emozioni.
    
    Monitora lo stato emotivo e decide quando l'agente deve contattare spontaneamente
    l'utente su Telegram/WhatsApp con messaggi contestuali generati da LLM.
    """
    
    # Configurazione default (definita come attributo di classe per essere disponibile prima)
    default_settings = {
        "proactive_enabled": True,
        "enabled_emotions": {
            "excitement": {"threshold": 0.7, "weight": 1.0},
            "anticipation": {"threshold": 0.6, "weight": 0.9},
            "curiosity": {"threshold": 0.8, "weight": 0.8},
            "flow_state": {"threshold": 0.75, "weight": 0.7},
            "confusion": {"threshold": 0.6, "weight": 0.5}
        },
        "base_interval_minutes": 10,
        "escalation_multipliers": [1, 3, 30, 180],  # 10min, 30min, 5h, 30h
        "quiet_hours": {"start": "23:00", "end": "07:00"},
        "default_channel": "telegram",
        "max_daily_proactive": 10
    }
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.expanduser("~/.openclaw/emotion_config.json")
        self.state_path = os.path.expanduser("~/.openclaw/proactive_state.json")
        
        # Carica configurazione
        self.config = self._load_config()
        
        # Stato proattivo
        self.state = self._load_state()
        

    
    def _load_config(self) -> Dict[str, Any]:
        """Carica configurazione proattiva dal file config principale."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                return config.get("proactive_settings", self.default_settings)
            return self.default_settings.copy()
        except Exception as e:
            logger.warning(f"Failed to load proactive config: {e}")
            return self.default_settings.copy()
    
    def _load_state(self) -> Dict[str, Any]:
        """Carica stato proattivo persistente."""
        default_state = {
            "last_proactive_timestamp": None,
            "current_escalation_level": 0,
            "consecutive_unanswered": 0,
            "daily_count": 0,
            "last_reset_date": datetime.now().strftime("%Y-%m-%d"),
            "messages_history": []
        }
        
        try:
            if os.path.exists(self.state_path):
                with open(self.state_path, 'r') as f:
                    state = json.load(f)
                # Verifica se è un nuovo giorno (reset daily count)
                today = datetime.now().strftime("%Y-%m-%d")
                if state.get("last_reset_date") != today:
                    state["daily_count"] = 0
                    state["last_reset_date"] = today
                return state
            return default_state
        except Exception as e:
            logger.warning(f"Failed to load proactive state: {e}")
            return default_state
    
    def _save_state(self):
        """Salva stato proattivo."""
        try:
            with open(self.state_path, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save proactive state: {e}")
    
    def is_enabled(self) -> bool:
        """Verifica se il comportamento proattivo è abilitato."""
        return self.config.get("proactive_enabled", True)
    
    def enable(self):
        """Abilita comportamento proattivo."""
        self.config["proactive_enabled"] = True
        self._save_config()
        logger.info("Proactive behavior enabled")
    
    def disable(self):
        """Disabilita comportamento proattivo."""
        self.config["proactive_enabled"] = False
        self._save_config()
        logger.info("Proactive behavior disabled")
    
    def _save_config(self):
        """Salva configurazione nel file principale."""
        try:
            main_config = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    main_config = json.load(f)
            
            main_config["proactive_settings"] = self.config
            
            with open(self.config_path, 'w') as f:
                json.dump(main_config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save proactive config: {e}")
    
    def should_trigger(self, emotional_state: Dict[str, Any]) -> tuple[bool, str, float]:
        """
        Determina se dovrebbe scattare un comportamento proattivo.
        
        Returns:
            tuple: (should_trigger, emotion_name, intensity)
        """
        if not self.is_enabled():
            return False, "", 0.0
        
        # Verifica quiet hours
        if self._is_quiet_hours():
            logger.debug("Quiet hours active, skipping proactive trigger")
            return False, "", 0.0
        
        # Verifica daily limit
        max_daily = self.config.get("max_daily_proactive", 10)
        if self.state["daily_count"] >= max_daily:
            logger.debug(f"Daily limit reached ({self.state['daily_count']}/{max_daily})")
            return False, "", 0.0
        
        # Verifica tempo minimo dall'ultimo trigger
        if not self._check_interval():
            return False, "", 0.0
        
        # Controlla emozioni
        enabled_emotions = self.config.get("enabled_emotions", self.default_settings["enabled_emotions"])
        primary_emotions = emotional_state.get("primary_emotions", {})
        complex_emotions = emotional_state.get("complex_emotions", {})
        
        # Combina tutte le emozioni
        all_emotions = {**primary_emotions, **complex_emotions}
        
        # Trova emozione con highest score che supera soglia
        best_emotion = None
        best_score = 0.0
        best_intensity = 0.0
        
        for emotion_name, config in enabled_emotions.items():
            intensity = all_emotions.get(emotion_name, 0)
            threshold = config.get("threshold", 0.5)
            weight = config.get("weight", 1.0)
            
            if intensity >= threshold:
                score = intensity * weight
                if score > best_score:
                    best_score = score
                    best_emotion = emotion_name
                    best_intensity = intensity
        
        if best_emotion:
            logger.info(f"Proactive trigger: {best_emotion} at {best_intensity:.2f} (score: {best_score:.2f})")
            return True, best_emotion, best_intensity
        
        return False, "", 0.0
    
    def _is_quiet_hours(self) -> bool:
        """Verifica se siamo in quiet hours."""
        quiet_hours = self.config.get("quiet_hours", {"start": "23:00", "end": "07:00"})
        start_str = quiet_hours.get("start", "23:00")
        end_str = quiet_hours.get("end", "07:00")
        
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        
        start_parts = start_str.split(":")
        end_parts = end_str.split(":")
        
        start_minutes = int(start_parts[0]) * 60 + int(start_parts[1])
        end_minutes = int(end_parts[0]) * 60 + int(end_parts[1])
        
        # Gestisce il caso in cui quiet hours attraversano la mezzanotte
        if start_minutes > end_minutes:
            # Es: 23:00 - 07:00
            return current_time >= start_minutes or current_time < end_minutes
        else:
            # Es: 01:00 - 05:00
            return start_minutes <= current_time < end_minutes
    
    def _check_interval(self) -> bool:
        """Verifica se è passato abbastanza tempo dall'ultimo trigger."""
        last_timestamp = self.state.get("last_proactive_timestamp")
        if not last_timestamp:
            return True
        
        last_time = datetime.fromisoformat(last_timestamp)
        now = datetime.now()
        elapsed = (now - last_time).total_seconds() / 60  # minuti
        
        # Calcola intervallo corrente basato su escalation level
        base_interval = self.config.get("base_interval_minutes", 10)
        multipliers = self.config.get("escalation_multipliers", [1, 3, 30, 180])
        
        escalation_level = min(self.state.get("current_escalation_level", 0), len(multipliers) - 1)
        current_multiplier = multipliers[escalation_level]
        required_interval = base_interval * current_multiplier
        
        logger.debug(f"Interval check: {elapsed:.1f}min / {required_interval}min (level {escalation_level})")
        
        return elapsed >= required_interval
    
    def mark_triggered(self, emotion: str, channel: str = None):
        """Marca che un trigger proattivo è stato attivato."""
        now = datetime.now()
        
        self.state["last_proactive_timestamp"] = now.isoformat()
        self.state["daily_count"] = self.state.get("daily_count", 0) + 1
        
        # Aggiungi a history
        message_record = {
            "timestamp": now.isoformat(),
            "emotion": emotion,
            "channel": channel or self.config.get("default_channel", "telegram"),
            "answered": False
        }
        self.state["messages_history"].append(message_record)
        
        # Mantieni solo ultimi 100 messaggi
        if len(self.state["messages_history"]) > 100:
            self.state["messages_history"] = self.state["messages_history"][-100:]
        
        self._save_state()
        logger.info(f"Proactive trigger marked: {emotion} via {channel}")
    
    def mark_answered(self):
        """Marca che l'utente ha risposto all'ultimo messaggio proattivo."""
        if self.state["messages_history"]:
            # Trova l'ultimo messaggio non risposto
            for msg in reversed(self.state["messages_history"]):
                if not msg.get("answered", False):
                    msg["answered"] = True
                    msg["answered_at"] = datetime.now().isoformat()
                    break
        
        # Reset escalation level
        old_level = self.state.get("current_escalation_level", 0)
        self.state["current_escalation_level"] = 0
        self.state["consecutive_unanswered"] = 0
        
        self._save_state()
        logger.info(f"User answered proactive message, escalation reset from level {old_level}")
    
    def mark_unanswered(self):
        """Marca che l'utente NON ha risposto, aumenta escalation."""
        self.state["consecutive_unanswered"] = self.state.get("consecutive_unanswered", 0) + 1
        
        # Incrementa escalation level
        old_level = self.state.get("current_escalation_level", 0)
        max_level = len(self.config.get("escalation_multipliers", [1, 3, 30, 180])) - 1
        self.state["current_escalation_level"] = min(old_level + 1, max_level)
        
        self._save_state()
        logger.info(f"User didn't answer, escalation increased: {old_level} -> {self.state['current_escalation_level']}")
    
    def get_status(self) -> Dict[str, Any]:
        """Restituisce stato corrente del sistema proattivo."""
        now = datetime.now()
        
        # Calcola tempo rimanente
        time_remaining = "N/A"
        if self.state.get("last_proactive_timestamp"):
            last_time = datetime.fromisoformat(self.state["last_proactive_timestamp"])
            base_interval = self.config.get("base_interval_minutes", 10)
            multipliers = self.config.get("escalation_multipliers", [1, 3, 30, 180])
            escalation_level = min(self.state.get("current_escalation_level", 0), len(multipliers) - 1)
            required_interval = base_interval * multipliers[escalation_level]
            
            elapsed = (now - last_time).total_seconds() / 60
            remaining = max(0, required_interval - elapsed)
            time_remaining = f"{int(remaining)} minutes"
        
        return {
            "enabled": self.is_enabled(),
            "current_escalation_level": self.state.get("current_escalation_level", 0),
            "consecutive_unanswered": self.state.get("consecutive_unanswered", 0),
            "daily_count": self.state.get("daily_count", 0),
            "daily_limit": self.config.get("max_daily_proactive", 10),
            "time_until_next": time_remaining,
            "quiet_hours_active": self._is_quiet_hours(),
            "quiet_hours": self.config.get("quiet_hours", {"start": "23:00", "end": "07:00"}),
            "default_channel": self.config.get("default_channel", "telegram"),
            "enabled_emotions": self.config.get("enabled_emotions", {})
        }
    
    def set_channel(self, channel: str) -> bool:
        """Cambia canale default."""
        if channel not in ["telegram", "whatsapp"]:
            return False
        
        self.config["default_channel"] = channel
        self._save_config()
        logger.info(f"Default channel changed to: {channel}")
        return True
    
    def set_quiet_hours(self, start: str, end: str) -> bool:
        """Configura quiet hours (formato HH:MM)."""
        try:
            # Validazione formato
            datetime.strptime(start, "%H:%M")
            datetime.strptime(end, "%H:%M")
            
            self.config["quiet_hours"] = {"start": start, "end": end}
            self._save_config()
            logger.info(f"Quiet hours set to: {start} - {end}")
            return True
        except ValueError:
            logger.error(f"Invalid time format: {start} or {end}")
            return False
    
    def set_threshold(self, emotion: str, threshold: float) -> bool:
        """Modifica soglia per un'emozione."""
        if not 0 <= threshold <= 1:
            return False
        
        enabled_emotions = self.config.get("enabled_emotions", self.default_settings["enabled_emotions"])
        
        if emotion not in enabled_emotions:
            # Aggiungi nuova emozione
            enabled_emotions[emotion] = {"threshold": threshold, "weight": 1.0}
        else:
            enabled_emotions[emotion]["threshold"] = threshold
        
        self.config["enabled_emotions"] = enabled_emotions
        self._save_config()
        logger.info(f"Threshold for {emotion} set to {threshold}")
        return True
    
    def check_and_update_unanswered(self) -> bool:
        """
        Controlla se l'ultimo messaggio è stato risposto.
        Da chiamare periodicamente per aggiornare escalation.
        
        Returns:
            bool: True se è passato abbastanza tempo per considerarlo non risposto
        """
        if not self.state["messages_history"]:
            return False
        
        last_msg = None
        for msg in reversed(self.state["messages_history"]):
            if not msg.get("answered", False):
                last_msg = msg
                break
        
        if not last_msg:
            return False
        
        # Controlla se è passato abbastanza tempo (30 minuti)
        msg_time = datetime.fromisoformat(last_msg["timestamp"])
        now = datetime.now()
        elapsed = (now - msg_time).total_seconds() / 60
        
        if elapsed >= 30 and not last_msg.get("marked_unanswered", False):
            last_msg["marked_unanswered"] = True
            self.mark_unanswered()
            return True
        
        return False
