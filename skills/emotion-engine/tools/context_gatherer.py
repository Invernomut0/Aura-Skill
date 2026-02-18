#!/usr/bin/env python3
"""
Context Gatherer - Raccoglie contesto per messaggi proattivi
Raccoglie dati da conversazioni, task e memoria
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger('emotion_engine')


class ContextGatherer:
    """
    Raccoglie contesto rilevante per generare messaggi proattivi personalizzati.
    
    Fonti:
    - Ultime conversazioni con l'utente
    - Task aperti nel task manager
    - Memoria vettoriale (se disponibile)
    - File recenti modificati
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.context_depth = self.config.get("context_depth", {
            "conversation_messages": 5,
            "task_list_items": 3,
            "memory_entries": 2
        })
        
        # Paths
        self.openclaw_dir = os.path.expanduser("~/.openclaw")
        self.memory_file = os.path.join(self.openclaw_dir, "current_emotional_state.json")
        self.interaction_history_file = os.path.join(self.openclaw_dir, "emotion_interactions.db")
    
    def gather_context(self, emotion: str, intensity: float) -> Dict[str, Any]:
        """
        Raccoglie contesto completo per un messaggio proattivo.
        
        Args:
            emotion: Nome dell'emozione triggerante
            intensity: Intensità dell'emozione
            
        Returns:
            Dict con tutto il contesto raccolto
        """
        logger.info(f"Gathering context for {emotion} at intensity {intensity:.2f}")
        
        context = {
            "emotion": emotion,
            "intensity": intensity,
            "timestamp": datetime.now().isoformat(),
            "conversation_context": self._gather_conversation_context(),
            "task_context": self._gather_task_context(),
            "memory_context": self._gather_memory_context(),
            "recent_topics": self._identify_recent_topics(),
            "pending_items": self._identify_pending_items()
        }
        
        logger.debug(f"Context gathered: {len(context)} sections")
        return context
    
    def _gather_conversation_context(self) -> List[Dict[str, Any]]:
        """Raccoglie ultime conversazioni dalla memoria emotiva."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    state = json.load(f)
                
                emotional_memory = state.get("emotional_memory", {})
                recent_interactions = emotional_memory.get("recent_interactions", [])
                
                # Prendi ultime N interazioni
                n = self.context_depth.get("conversation_messages", 5)
                recent = recent_interactions[-n:] if len(recent_interactions) > n else recent_interactions
                
                # Estrai testo rilevante
                conversations = []
                for interaction in recent:
                    text = interaction.get("text", "")
                    if text and len(text) > 10:  # Ignora messaggi troppo corti
                        conversations.append({
                            "text": text[:200],  # Tronca messaggi lunghi
                            "timestamp": interaction.get("timestamp", ""),
                            "sentiment": interaction.get("sentiment", {})
                        })
                
                return conversations
            
            return []
        except Exception as e:
            logger.warning(f"Failed to gather conversation context: {e}")
            return []
    
    def _gather_task_context(self) -> List[Dict[str, Any]]:
        """Raccoglie task aperti dal task manager."""
        try:
            # Cerca file task nel workspace
            workspace_dir = os.path.join(self.openclaw_dir, "workspace")
            task_files = []
            
            if os.path.exists(workspace_dir):
                for root, dirs, files in os.walk(workspace_dir):
                    for file in files:
                        if file.endswith(('.task', '.todo', 'tasks.json')):
                            task_files.append(os.path.join(root, file))
            
            tasks = []
            n = self.context_depth.get("task_list_items", 3)
            
            # Prova a leggere task dai file trovati
            for task_file in task_files[:n]:
                try:
                    with open(task_file, 'r') as f:
                        content = f.read()
                        # Estrai prime righe non vuote
                        lines = [l.strip() for l in content.split('\n') if l.strip()][:5]
                        if lines:
                            tasks.append({
                                "file": os.path.basename(task_file),
                                "content": lines,
                                "source": task_file
                            })
                except:
                    continue
            
            # Se non trova file, cerca nella memoria
            if not tasks and os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    state = json.load(f)
                
                # Cerca task nelle interazioni recenti
                emotional_memory = state.get("emotional_memory", {})
                recent_interactions = emotional_memory.get("recent_interactions", [])
                
                task_keywords = ["task", "todo", "da fare", "completare", "implementare", "sviluppare"]
                
                for interaction in recent_interactions[-10:]:
                    text = interaction.get("text", "").lower()
                    for keyword in task_keywords:
                        if keyword in text:
                            tasks.append({
                                "source": "conversation",
                                "content": [interaction.get("text", "")[:150]],
                                "extracted": True
                            })
                            break
                    if len(tasks) >= n:
                        break
            
            return tasks[:n]
        
        except Exception as e:
            logger.warning(f"Failed to gather task context: {e}")
            return []
    
    def _gather_memory_context(self) -> List[Dict[str, Any]]:
        """Raccoglie entrate rilevanti dalla memoria."""
        try:
            if not os.path.exists(self.memory_file):
                return []
            
            with open(self.memory_file, 'r') as f:
                state = json.load(f)
            
            context = []
            n = self.context_depth.get("memory_entries", 2)
            
            # Raccogli pattern apprese
            emotional_memory = state.get("emotional_memory", {})
            learned_patterns = emotional_memory.get("learned_patterns", {})
            
            if learned_patterns:
                # Prendi pattern più recenti o rilevanti
                patterns = list(learned_patterns.items())[-n:]
                for key, pattern in patterns:
                    context.append({
                        "type": "learned_pattern",
                        "key": key,
                        "value": str(pattern)[:200]
                    })
            
            # Raccogli emozioni dominanti recenti
            dominant_history = state.get("dominant_emotions_history", [])
            if dominant_history:
                recent_dominant = dominant_history[-3:]
                context.append({
                    "type": "dominant_emotions",
                    "history": recent_dominant
                })
            
            return context
        
        except Exception as e:
            logger.warning(f"Failed to gather memory context: {e}")
            return []
    
    def _identify_recent_topics(self) -> List[str]:
        """Identifica topic recenti dalle conversazioni."""
        try:
            conversations = self._gather_conversation_context()
            if not conversations:
                return []
            
            # Parole chiave tecniche/comuni
            tech_keywords = [
                "codice", "code", "programming", "python", "javascript", "database",
                "api", "server", "docker", "kubernetes", "debug", "bug", "error",
                "test", "testing", "refactoring", "optimization", "performance",
                "ui", "frontend", "backend", "fullstack", "devops", "git",
                "project", "progetto", "task", "feature", "implementazione"
            ]
            
            found_topics = []
            for conv in conversations:
                text = conv.get("text", "").lower()
                for keyword in tech_keywords:
                    if keyword in text and keyword not in found_topics:
                        found_topics.append(keyword)
            
            return found_topics[:5]  # Max 5 topic
        
        except Exception as e:
            logger.warning(f"Failed to identify recent topics: {e}")
            return []
    
    def _identify_pending_items(self) -> List[str]:
        """Identifica elementi pendenti o bloccati."""
        try:
            pending = []
            
            # Cerca nelle conversazioni segnali di problemi
            conversations = self._gather_conversation_context()
            problem_keywords = ["bloccato", "stuck", "error", "errore", "bug", "non funziona", "broken"]
            
            for conv in conversations:
                text = conv.get("text", "").lower()
                for keyword in problem_keywords:
                    if keyword in text:
                        snippet = conv.get("text", "")[:100]
                        pending.append(f"Possible issue: {snippet}...")
                        break
            
            return pending[:3]
        
        except Exception as e:
            logger.warning(f"Failed to identify pending items: {e}")
            return []
    
    def format_context_for_llm(self, context: Dict[str, Any]) -> str:
        """
        Formatta il contesto per essere usato in un prompt LLM.
        
        Returns:
            Stringa formattata con tutto il contesto
        """
        lines = []
        
        lines.append("=" * 50)
        lines.append("CONTESTO PER MESSAGGIO PROATTIVO")
        lines.append("=" * 50)
        
        # Emozione corrente
        lines.append(f"\nEMOZIONE TRIGGERANTE: {context['emotion'].upper()}")
        lines.append(f"Intensità: {context['intensity']:.2f}")
        
        # Topic recenti
        topics = context.get("recent_topics", [])
        if topics:
            lines.append(f"\nTOPIC RECENTI: {', '.join(topics)}")
        
        # Task aperti
        tasks = context.get("task_context", [])
        if tasks:
            lines.append("\nTASK APERTI:")
            for i, task in enumerate(tasks, 1):
                content = task.get("content", [])
                if content:
                    lines.append(f"  {i}. {content[0]}")
        
        # Elementi pendenti
        pending = context.get("pending_items", [])
        if pending:
            lines.append("\nELEMENTI PENDENTI/PROBLEMI:")
            for item in pending:
                lines.append(f"  - {item}")
        
        # Ultime conversazioni
        conversations = context.get("conversation_context", [])
        if conversations:
            lines.append("\nULTIME CONVERSAZIONI:")
            for i, conv in enumerate(conversations[-3:], 1):  # Ultime 3
                text = conv.get("text", "")
                if text:
                    lines.append(f"  {i}. \"{text[:150]}...\"")
        
        lines.append("\n" + "=" * 50)
        
        return "\n".join(lines)
