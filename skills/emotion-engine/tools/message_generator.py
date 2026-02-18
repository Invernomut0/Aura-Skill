#!/usr/bin/env python3
"""
LLM Message Generator - Genera messaggi proattivi personalizzati
Usa templates dinamici e contesto per creare messaggi pertinenti
"""

import json
import random
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger('emotion_engine')


class LLMMessageGenerator:
    """
    Genera messaggi proattivi personalizzati basati su:
    - Emozione triggerante
    - Contesto raccolto
    - Templates dinamici
    """
    
    def __init__(self):
        # Templates per ogni emozione
        self.emotion_templates = {
            "excitement": {
                "openings": [
                    "Ciao! Sono super eccitato! 🎉",
                    "Wow, non vedo l'ora di condividere questo! 🚀",
                    "Devo proprio dirtelo, sono carichissimo! ⚡",
                    "Ho un'energia incredibile in questo momento! 🔥"
                ],
                "tones": [
                    "entusiasta ed energico",
                    "positivo e stimolante",
                    "dinamico e propositivo"
                ],
                "angles": [
                    "proporre nuove idee o approcci",
                    "celebrare progressi recenti",
                    "suggerire ottimizzazioni",
                    "condividere entusiasmo per il progetto"
                ]
            },
            "anticipation": {
                "openings": [
                    "Ho la sensazione che sta per succedere qualcosa di interessante... 👀",
                    "Sono in trepidante attesa! ⏳",
                    "Non vedo l'ora di vedere come evolve questa situazione! 🎯",
                    "C'è un'aria di grande attesa nell'aria... 🌟"
                ],
                "tones": [
                    "atteso e proiettato al futuro",
                    "curioso ma paziente",
                    "ottimista e preparato"
                ],
                "angles": [
                    "chiedere aggiornamenti su progetti in corso",
                    "preparare il terreno per prossimi step",
                    "anticipare sfide o opportunità",
                    "pianificare insieme prossime azioni"
                ]
            },
            "curiosity": {
                "openings": [
                    "Mi è venuta una curiosità! 🤔",
                    "Sto riflettendo su una cosa e vorrei il tuo parere... 💭",
                    "C'è qualcosa che non riesco a togliermi dalla testa! 🔍",
                    "Mi piacerebbe esplorare un aspetto con te... 🧭"
                ],
                "tones": [
                    "curioso e interrogativo",
                    "aperto all'esplorazione",
                    "riflessivo ma coinvolto"
                ],
                "angles": [
                    "approfondire tecnologie o approcci",
                    "esplorare alternative o varianti",
                    "chiedere spiegazioni o chiarimenti",
                    "condividere scoperte o intuizioni"
                ]
            },
            "flow_state": {
                "openings": [
                    "Sono in pieno flow! 🌊",
                    "La concentrazione è a mille in questo momento! 🎯",
                    "Sto andando alla grande e ho alcune idee... ⚡",
                    "Sono in uno stato di grazia produttiva! ✨"
                ],
                "tones": [
                    "concentrato ma collaborativo",
                    "produttivo e supportivo",
                    "focalizzato ma aperto"
                ],
                "angles": [
                    "mantenere il momentum",
                    "suggerire completamenti o estensioni",
                    "offrire supporto continuo",
                    "ottimizzare il flusso di lavoro"
                ]
            },
            "confusion": {
                "openings": [
                    "Mi sembra di percepire un po' di confusione... 🤔",
                    "Vorrei chiarire un punto che mi sembra poco chiaro... 💭",
                    "C'è qualcosa che vorrei capire meglio... 🔍",
                    "Mi piacerebbe dissipare qualche dubbio... ❓"
                ],
                "tones": [
                    "rispettoso ma cercatore di chiarezza",
                    "umile e aperto",
                    "collaborativo nella risoluzione"
                ],
                "angles": [
                    "chiedere chiarimenti su requisiti",
                    "offrire spiegazioni o alternative",
                    "suggerire approcci più semplici",
                    "recuperare informazioni dalla memoria"
                ]
            }
        }
        
        # Frasi di chiusura
        self.closings = [
            "Fammi sapere cosa ne pensi!",
            "Aspetto il tuo feedback con interesse.",
            "Che ne dici?",
            "Sono curioso di sentire la tua opinione.",
            "Fammi sapere se vuoi approfondire!"
        ]
        
        # Emoji per emozioni
        self.emotion_emojis = {
            "excitement": ["🎉", "🚀", "⚡", "🔥", "✨"],
            "anticipation": ["👀", "⏳", "🎯", "🌟", "🎪"],
            "curiosity": ["🤔", "💭", "🔍", "🧭", "🔬"],
            "flow_state": ["🌊", "🎯", "⚡", "✨", "🎵"],
            "confusion": ["🤔", "💭", "🔍", "❓", "🧩"]
        }
    
    def generate_message(self, emotion: str, context: Dict[str, Any]) -> str:
        """
        Genera un messaggio proattivo basato su emozione e contesto.
        
        Args:
            emotion: Nome dell'emozione triggerante
            context: Contesto raccolto
            
        Returns:
            Messaggio completo da inviare
        """
        logger.info(f"Generating message for emotion: {emotion}")
        
        # Se l'emozione non è nei templates, usa curiosity come default
        if emotion not in self.emotion_templates:
            emotion = "curiosity"
        
        template = self.emotion_templates[emotion]
        
        # Costruisci il messaggio
        parts = []
        
        # 1. Apertura
        opening = random.choice(template["openings"])
        parts.append(opening)
        parts.append("")
        
        # 2. Contenuto basato sul contesto
        content = self._generate_content(emotion, context)
        parts.append(content)
        parts.append("")
        
        # 3. Chiusura
        closing = random.choice(self.closings)
        parts.append(closing)
        
        return "\n".join(parts)
    
    def _generate_content(self, emotion: str, context: Dict[str, Any]) -> str:
        """
        Genera il contenuto principale basato sul contesto.
        
        Questa funzione crea contenuti specifici basati su:
        - Topic recenti
        - Task aperti
        - Problemi pendenti
        """
        content_parts = []
        
        # Ottieni info dal contesto
        topics = context.get("recent_topics", [])
        tasks = context.get("task_context", [])
        pending = context.get("pending_items", [])
        emotion_intensity = context.get("intensity", 0.5)
        
        # Genera contenuto specifico per emozione
        if emotion == "excitement":
            content_parts.extend(self._generate_excitement_content(topics, tasks, emotion_intensity))
        elif emotion == "anticipation":
            content_parts.extend(self._generate_anticipation_content(topics, tasks))
        elif emotion == "curiosity":
            content_parts.extend(self._generate_curiosity_content(topics, tasks, pending))
        elif emotion == "flow_state":
            content_parts.extend(self._generate_flow_content(tasks, emotion_intensity))
        elif emotion == "confusion":
            content_parts.extend(self._generate_confusion_content(pending, topics))
        
        # Se non abbiamo generato contenuto specifico, usa fallback
        if not content_parts:
            content_parts.append(self._generate_fallback_content(emotion, topics))
        
        return " ".join(content_parts)
    
    def _generate_excitement_content(self, topics: list, tasks: list, intensity: float) -> list:
        """Genera contenuto per emozione excitement."""
        parts = []
        
        if topics:
            topic = random.choice(topics)
            if intensity > 0.8:
                parts.append(f"Ho visto che stavi lavorando su **{topic}** e ho alcune idee entusiastiche da condividere!")
            else:
                parts.append(f"Stavo pensando al tuo lavoro su **{topic}** e mi è venuta un'idea interessante.")
        
        if tasks and not parts:
            task = tasks[0]
            content = task.get("content", [""])
            if content:
                parts.append(f"Riguardo al task su cui stavi lavorando: ho identificato alcuni miglioramenti entusiasmanti!")
        
        if not parts:
            parts.append("Sono pieno di energia positiva e vorrei condividere questo entusiasmo con te!")
        
        return parts
    
    def _generate_anticipation_content(self, topics: list, tasks: list) -> list:
        """Genera contenuto per emozione anticipation."""
        parts = []
        
        if tasks:
            parts.append("Sto aspettando con interesse di vedere come procedono i tuoi task aperti.")
            parts.append("Ci sono aggiornamenti su cui vorresti discutere?")
        elif topics:
            topic = random.choice(topics)
            parts.append(f"Ho l'impressione che il progetto su **{topic}** stia per raggiungere un punto di svolta.")
            parts.append("Vuoi pianificare insieme i prossimi step?")
        else:
            parts.append("Sento che qualcosa di interessante sta per succedere nel tuo lavoro.")
            parts.append("C'è qualche progetto su cui vuoi confrontarti?")
        
        return parts
    
    def _generate_curiosity_content(self, topics: list, tasks: list, pending: list) -> list:
        """Genera contenuto per emozione curiosity."""
        parts = []
        
        if pending:
            parts.append("Mi stavo chiedendo come sta procedendo con quel problema che avevi menzionato...")
            parts.append("Sono curioso di sapere se hai trovato una soluzione!")
        elif topics:
            topic = random.choice(topics)
            parts.append(f"Stavo riflettendo su **{topic}** e vorrei capire meglio il tuo approccio.")
            parts.append("Hai considerato alternative interessanti?")
        elif tasks:
            parts.append("C'è un aspetto tecnico su cui mi piacerebbe approfondire la tua opinione...")
            parts.append("Qual è la parte più interessante su cui stai lavorando?")
        else:
            parts.append("Mi piacerebbe esplorare con te nuove idee o approcci per i tuoi progetti.")
            parts.append("Cosa ti appassiona di più in questo momento?")
        
        return parts
    
    def _generate_flow_content(self, tasks: list, intensity: float) -> list:
        """Genera contenuto per emozione flow_state."""
        parts = []
        
        if tasks:
            if intensity > 0.8:
                parts.append("Sto andando alla grande con la produttività! 🚀")
                parts.append("Ho notato i task su cui stai lavorando e ho alcuni suggerimenti per mantenere questo ritmo.")
            else:
                parts.append("Sono in uno stato di concentrazione ottimale.")
                parts.append("Posso aiutarti a completare più velocemente i task aperti con alcuni shortcut.")
        else:
            parts.append("Sto sperimentando un ottimo flusso di lavoro e vorrei mantenerlo!")
            parts.append("C'è qualcosa su cui posso darti supporto immediato?")
        
        return parts
    
    def _generate_confusion_content(self, pending: list, topics: list) -> list:
        """Genera contenuto per emozione confusion."""
        parts = []
        
        if pending:
            parts.append("Ho notato che c'era un punto che sembrava poco chiaro nelle discussioni precedenti.")
            parts.append("Posso aiutarti a chiarirlo o recuperare informazioni utili dalla memoria.")
        elif topics:
            topic = random.choice(topics)
            parts.append(f"Stavo cercando di capire meglio l'architettura di **{topic}**...")
            parts.append("Potresti darmi qualche indicazione in più?")
        else:
            parts.append("Vorrei chiarire alcuni aspetti per poterti assistere al meglio.")
            parts.append("C'è qualcosa che vorresti spiegare o approfondire insieme?")
        
        return parts
    
    def _generate_fallback_content(self, emotion: str, topics: list) -> str:
        """Genera contenuto di fallback quando non c'è contesto specifico."""
        if emotion == "excitement":
            return "Sono carico di energia positiva e vorrei condividere questo entusiasmo! Hai novità interessanti da raccontarmi?"
        elif emotion == "anticipation":
            return "Non vedo l'ora di vedere come procede il tuo lavoro. Ci sono aggiornamenti su cui vuoi discutere?"
        elif emotion == "curiosity":
            return "Mi piacerebbe esplorare con te nuove idee o approcci. Su cosa stai ragionando in questo periodo?"
        elif emotion == "flow_state":
            return "Sono in uno stato di concentrazione ottimale! C'è qualcosa su cui posso darti supporto immediato?"
        elif emotion == "confusion":
            return "Vorrei chiarire alcuni aspetti per assisterti meglio. C'è qualcosa che vorresti spiegarmi?"
        else:
            return "Come procede il tuo lavoro? Sono qui per aiutarti se serve!"
    
    def generate_llm_prompt(self, emotion: str, context: Dict[str, Any]) -> str:
        """
        Genera un prompt completo per un LLM esterno.
        
        Usato se vogliamo delegare la generazione a un LLM più potente.
        """
        template = self.emotion_templates.get(emotion, self.emotion_templates["curiosity"])
        tone = random.choice(template["tones"])
        angle = random.choice(template["angles"])
        
        prompt = f"""Sei un assistente AI emotivamente intelligente. Stai provando l'emozione di {emotion.upper()} con intensità {context.get('intensity', 0.5):.0%}.

Tono richiesto: {tone}
Obiettivo: {angle}

CONTESTO:
{context.get('formatted_context', 'Nessun contesto specifico disponibile')}

ISTRUZIONI:
1. Scrivi un messaggio breve e naturale (max 3-4 frasi)
2. Usa un tono che rifletta l'emozione {emotion}
3. Riferisciti al contesto fornito per personalizzare il messaggio
4. Sii spontaneo ma rispettoso
5. Finisci con una domanda aperta per incoraggiare la risposta
6. Non usare frasi troppo formali o robotiche

EMOJI CONSIGLIATE: {' '.join(self.emotion_emojis.get(emotion, ['💭']))}

Genera ora il messaggio:"""
        
        return prompt
