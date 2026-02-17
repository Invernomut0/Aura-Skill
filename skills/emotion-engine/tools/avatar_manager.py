#!/usr/bin/env python3
"""
Avatar Manager for OpenClaw Emotional Intelligence System.
Dynamically updates the agent's avatar based on the current emotional state.
"""

import os
import json
import shutil
from typing import Dict, Optional, Tuple
from pathlib import Path

# Emotion to avatar mapping
EMOTION_AVATAR_MAP = {
    # Primary emotions
    "joy": "AURA_joy.png",
    "sadness": "AURA_sad.png",
    "anger": "AURA_angry.png",
    "fear": "AURA_fear.png",
    "surprise": "AURA_surprise.png",
    "disgust": "AURA_disgust.png",
    "curiosity": "AURA_curiosity.png",
    "trust": "AURA_trust.png",
    
    # Complex emotions
    "excitement": "AURA_excitement.png",
    "frustration": "AURA_frustration.png",
    "satisfaction": "AURA_satisfaction.png",
    "confusion": "AURA_confusion.png",
    "anticipation": "AURA_anticipation.png",
    "empathy": "AURA_empathy.png",
    "flow_state": "AURA_flow_state.png",
}

class AvatarManager:
    """Gestisce il cambio dinamico dell'avatar in base allo stato emotivo."""
    
    def __init__(self, 
                 assets_dir: str = None, 
                 openclaw_config_path: str = None,
                 workspace_avatar_dir: str = None):
        """
        Inizializza l'AvatarManager.
        
        Args:
            assets_dir: Directory contenente gli avatar (default: AURA_Skill/assets)
            openclaw_config_path: Path al file di configurazione OpenClaw
            workspace_avatar_dir: Directory nel workspace dove copiare gli avatar
        """
        # Determina il path della cartella assets
        if assets_dir is None:
            # Assume che questo script sia in skills/emotion-engine/tools/
            skill_dir = Path(__file__).parent.parent.parent.parent
            assets_dir = skill_dir / "assets"
        self.assets_dir = Path(assets_dir)
        
        # Path al file di configurazione OpenClaw
        if openclaw_config_path is None:
            openclaw_config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        self.openclaw_config_path = Path(openclaw_config_path)
        
        # Directory nel workspace per gli avatar
        if workspace_avatar_dir is None:
            workspace_avatar_dir = os.path.expanduser("~/.openclaw/workspace/avatars")
        self.workspace_avatar_dir = Path(workspace_avatar_dir)
        
        # Crea la directory avatars nel workspace se non esiste
        self.workspace_avatar_dir.mkdir(parents=True, exist_ok=True)
        
        # Avatar corrente
        self.current_avatar = None
        
    def get_dominant_emotion(self, emotional_state: Dict) -> Tuple[str, float]:
        """
        Determina l'emozione dominante dallo stato emotivo.
        
        Args:
            emotional_state: Dizionario dello stato emotivo
            
        Returns:
            Tupla (emotion_name, intensity)
        """
        # Combina emozioni primarie e complesse
        all_emotions = {}
        
        if "primary_emotions" in emotional_state:
            all_emotions.update(emotional_state["primary_emotions"])
        
        if "complex_emotions" in emotional_state:
            # Le emozioni complesse hanno priorità se abbastanza intense
            complex = emotional_state["complex_emotions"]
            # Moltiplica per 1.2 per dare priorità alle emozioni complesse
            for emotion, intensity in complex.items():
                if intensity > 0.15:  # Soglia minima per considerare un'emozione complessa
                    all_emotions[emotion] = intensity * 1.2
        
        if not all_emotions:
            return "curiosity", 0.5  # Default
        
        # Trova l'emozione con intensità maggiore
        dominant_emotion = max(all_emotions.items(), key=lambda x: x[1])
        return dominant_emotion[0], dominant_emotion[1]
    
    def get_avatar_for_emotion(self, emotion: str) -> Optional[str]:
        """
        Ottiene il nome del file avatar per una determinata emozione.
        
        Args:
            emotion: Nome dell'emozione
            
        Returns:
            Nome del file avatar o None se non trovato
        """
        return EMOTION_AVATAR_MAP.get(emotion)
    
    def copy_avatar_to_workspace(self, avatar_filename: str) -> bool:
        """
        Copia l'avatar dalla cartella assets al workspace.
        
        Args:
            avatar_filename: Nome del file avatar
            
        Returns:
            True se l'operazione ha successo
        """
        source_path = self.assets_dir / avatar_filename
        dest_path = self.workspace_avatar_dir / "current_avatar.png"
        
        if not source_path.exists():
            print(f"⚠️  Avatar file not found: {source_path}")
            return False
        
        try:
            shutil.copy2(source_path, dest_path)
            print(f"✅ Avatar copied: {avatar_filename} -> {dest_path}")
            return True
        except Exception as e:
            print(f"❌ Error copying avatar: {e}")
            return False
    
    def update_openclaw_config(self, avatar_path: str) -> bool:
        """
        Aggiorna il file di configurazione OpenClaw con il nuovo avatar.
        
        Args:
            avatar_path: Path relativo al workspace dell'avatar
            
        Returns:
            True se l'operazione ha successo
        """
        try:
            # Leggi il file di configurazione attuale
            if not self.openclaw_config_path.exists():
                print(f"⚠️  OpenClaw config not found: {self.openclaw_config_path}")
                return False
            
            with open(self.openclaw_config_path, 'r') as f:
                config = json.load(f)
            
            # Assicurati che esistano le sezioni necessarie
            if "agents" not in config:
                config["agents"] = {}
            if "list" not in config["agents"]:
                config["agents"]["list"] = [{"id": "main", "default": True}]
            
            # Trova l'agent principale (default o primo)
            main_agent = None
            for agent in config["agents"]["list"]:
                if agent.get("default", False) or agent.get("id") == "main":
                    main_agent = agent
                    break
            
            if main_agent is None and config["agents"]["list"]:
                main_agent = config["agents"]["list"][0]
            
            if main_agent is None:
                print("⚠️  No agent found in config")
                return False
            
            # Aggiorna l'avatar
            if "identity" not in main_agent:
                main_agent["identity"] = {}
            
            main_agent["identity"]["avatar"] = avatar_path
            
            # Salva il file di configurazione
            with open(self.openclaw_config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ OpenClaw config updated with avatar: {avatar_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating OpenClaw config: {e}")
            return False
    
    def update_avatar_from_emotion(self, emotional_state: Dict) -> Tuple[bool, str, str]:
        """
        Aggiorna l'avatar in base allo stato emotivo.
        
        Args:
            emotional_state: Dizionario dello stato emotivo
            
        Returns:
            Tupla (success, emotion, avatar_filename)
        """
        # Determina l'emozione dominante
        emotion, intensity = self.get_dominant_emotion(emotional_state)
        
        # Ottieni il file avatar corrispondente
        avatar_filename = self.get_avatar_for_emotion(emotion)
        
        if not avatar_filename:
            print(f"⚠️  No avatar found for emotion: {emotion}")
            return False, emotion, None
        
        # Se l'avatar è già quello corrente, non fare nulla
        if self.current_avatar == avatar_filename:
            print(f"ℹ️  Avatar already set to {emotion}: {avatar_filename}")
            return True, emotion, avatar_filename
        
        # Copia l'avatar nel workspace
        if not self.copy_avatar_to_workspace(avatar_filename):
            return False, emotion, avatar_filename
        
        # Aggiorna la configurazione OpenClaw
        avatar_workspace_path = "avatars/current_avatar.png"
        if not self.update_openclaw_config(avatar_workspace_path):
            return False, emotion, avatar_filename
        
        # Aggiorna l'avatar corrente
        self.current_avatar = avatar_filename
        
        print(f"🎭 Avatar changed to {emotion} (intensity: {intensity:.2f}): {avatar_filename}")
        return True, emotion, avatar_filename
    
    def get_current_avatar_info(self) -> Dict:
        """
        Ottiene informazioni sull'avatar corrente.
        
        Returns:
            Dizionario con informazioni sull'avatar
        """
        info = {
            "current_avatar": self.current_avatar,
            "workspace_avatar_path": str(self.workspace_avatar_dir / "current_avatar.png"),
            "assets_dir": str(self.assets_dir),
            "available_avatars": list(EMOTION_AVATAR_MAP.keys())
        }
        
        # Controlla se l'avatar corrente esiste nel workspace
        current_path = self.workspace_avatar_dir / "current_avatar.png"
        info["avatar_exists"] = current_path.exists()
        
        return info
    
    def list_available_avatars(self) -> Dict[str, str]:
        """
        Elenca tutti gli avatar disponibili.
        
        Returns:
            Dizionario {emotion: avatar_filename}
        """
        available = {}
        for emotion, filename in EMOTION_AVATAR_MAP.items():
            avatar_path = self.assets_dir / filename
            if avatar_path.exists():
                available[emotion] = filename
        
        return available
    
    def force_update_avatar(self, emotion: str) -> Tuple[bool, str]:
        """
        Forza l'aggiornamento dell'avatar per una specifica emozione.
        
        Args:
            emotion: Nome dell'emozione
            
        Returns:
            Tupla (success, message)
        """
        avatar_filename = self.get_avatar_for_emotion(emotion)
        
        if not avatar_filename:
            return False, f"No avatar found for emotion: {emotion}"
        
        # Reset current avatar per forzare l'aggiornamento
        self.current_avatar = None
        
        # Copia l'avatar
        if not self.copy_avatar_to_workspace(avatar_filename):
            return False, f"Failed to copy avatar: {avatar_filename}"
        
        # Aggiorna la configurazione
        avatar_workspace_path = "avatars/current_avatar.png"
        if not self.update_openclaw_config(avatar_workspace_path):
            return False, "Failed to update OpenClaw config"
        
        self.current_avatar = avatar_filename
        
        return True, f"Avatar forced to {emotion}: {avatar_filename}"


# Funzioni di utilità per l'integrazione con emotion_tool.py
def update_avatar_from_emotional_state(emotional_state: Dict) -> Tuple[bool, str, str]:
    """
    Funzione di utilità per aggiornare l'avatar dallo stato emotivo.
    
    Args:
        emotional_state: Dizionario dello stato emotivo
        
    Returns:
        Tupla (success, emotion, avatar_filename)
    """
    manager = AvatarManager()
    return manager.update_avatar_from_emotion(emotional_state)


def get_avatar_info() -> Dict:
    """
    Funzione di utilità per ottenere informazioni sull'avatar corrente.
    
    Returns:
        Dizionario con informazioni sull'avatar
    """
    manager = AvatarManager()
    return manager.get_avatar_info()


def list_avatars() -> Dict[str, str]:
    """
    Funzione di utilità per elencare tutti gli avatar disponibili.
    
    Returns:
        Dizionario {emotion: avatar_filename}
    """
    manager = AvatarManager()
    return manager.list_available_avatars()


if __name__ == "__main__":
    # Test del sistema
    print("🎭 Avatar Manager Test")
    print("=" * 50)
    
    manager = AvatarManager()
    
    # Lista avatar disponibili
    print("\n📋 Available Avatars:")
    available = manager.list_available_avatars()
    for emotion, filename in available.items():
        print(f"  • {emotion}: {filename}")
    
    # Test aggiornamento avatar
    print("\n🧪 Testing avatar update...")
    test_state = {
        "primary_emotions": {
            "joy": 0.8,
            "curiosity": 0.6,
            "trust": 0.5
        },
        "complex_emotions": {
            "excitement": 0.7,
            "satisfaction": 0.4
        }
    }
    
    success, emotion, avatar = manager.update_avatar_from_emotion(test_state)
    if success:
        print(f"\n✅ Test successful! Avatar set to '{emotion}': {avatar}")
    else:
        print(f"\n❌ Test failed for emotion: {emotion}")
    
    # Info avatar corrente
    print("\n📊 Current Avatar Info:")
    info = manager.get_current_avatar_info()
    for key, value in info.items():
        print(f"  • {key}: {value}")
