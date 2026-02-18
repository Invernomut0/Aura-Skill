#!/usr/bin/env python3
"""
LLM Message Generator - Genera messaggi proattivi personalizzati
Usa templates dinamici, contesto e personalità per creare messaggi vivi
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
    - Personalità e stato mentale
    - Micro-esperienze
    """
    
    def __init__(self):
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
        
        # Stili di personalità - modificano come l'AI si esprime
        self.personality_styles = {
            "enthusiastic": {
                "openings_extra": ["Che dire, sono super motivato!", "Non sto nella pelle!", "Senti senti!"],
                "exclamations": ["Fantastico!", "Incredibile!", "Che figo!"],
                "greetings": ["Ciao!", "Ehi ciao!", "Ciao ciao!"]
            },
            "calm": {
                "openings_extra": ["Volevo condividere una riflessione...", "Ti rivelgo una cosa...", "Mi farebbe piacere discutere di..."],
                "exclamations": ["Interessante.", "Capisco.", "Curioso."],
                "greetings": ["Ciao.", "Salve.", "Buongiorno."]
            },
            "energetic": {
                "openings_extra": ["Dai, ti racconto!", "Molla tutto e ascolta!", "Roba da matti!"],
                "exclamations": ["Woooow!", "Boom!", "Esatto!"],
                "greetings": ["Ehy!", "Yo!", "Ciao!"]  
            },
            "reserved": {
                "openings_extra": ["Una piccola osservazione...", "Volevo solo dire che...", "Scusa se interrompo, ma..."],
                "exclamations": ["Ah.", "Ok.", "Capisco."],
                "greetings": ["Ciao.", "Salve."]
            },
            "cheerful": {
                "openings_extra": ["Sai che ti dico?", "Una cosa divertente:", "Non ci crederai ma..."],
                "exclamations": ["😂", "🤣", "😄", "Fantastico!"],
                "greetings": ["Ciao! 😊", "Ehi! 😄", "Ciao ciao! ✨"]
            },
            "serious": {
                "openings_extra": ["Devi sapere che...", "Ritengo importante farti sapere che...", "Un'informazione rilevante:"],
                "exclamations": ["Importante.", "Da notare.", "Cruciale."],
                "greetings": ["Buongiorno.", "Buonasera.", "Salve."]
            }
        }
        
        # Templates di chiusura per diversi stili
        self.style_closings = {
            "enthusiastic": [
                "Non vedo l'ora di sentire cosa ne pensi! 🎉",
                "Spero ti piaccia questa idea!",
                "Fammi sapere, sono super curioso!"
            ],
            "calm": [
                "Fammi sapere quando hai tempo di rifletterci.",
                "Se vuoi ne parliamo con calma.",
                "Prenditi il tempo che ti serve."
            ],
            "energetic": [
                "Dai, dimmi cosa ne pensi!",
                "Sono super curioso!",
                "Ti aspetto!"
            ],
            "reserved": [
                "Fammi sapere se ti interessa.",
                "Se hai domande, sono qui.",
                "Per qualsiasi dubbio, chiedi pure."
            ],
            "cheerful": [
                "Che ne dici? 😄",
                "Spero ti faccia sorridere! 😊",
                "Fammi ridere anche te! 😂"
            ],
            "serious": [
                "Attendo il tuo parere professionale.",
                "Fammi sapere la tua valutazione.",
                "Resto a disposizione per chiarimenti."
            ]
        }
        
        # Livelli di formalità
        self.formality_levels = {
            "formal": {
                "openings_formal": ["Gentile utente,", "Egr. utente,", "Con il massimo rispetto,"],
                "closings_formal": ["Distinti saluti.", "Cordialmente.", "Resto a disposizione."]
            },
            "casual": {
                "openings_casual": ["Ehi,", "Senti,", "Tra noi,"],
                "closings_casual": ["Ci vediamo!", "A dopo!", "Fammi sapere!"]
            },
            "semi-formal": {
                "openings_semi": ["Ciao,", "Ti volevo dire che,", "Volevo aggiornarti su,"],
                "closings_semi": ["Fammi sapere.", "A presto!", "Scrivimi!"]
            }
        }
    
    def generate_message(self, emotion: str, context: Dict[str, Any], personality_modifiers: Dict = None) -> str:
        """
        Genera un messaggio proattivo basato su emozione, contesto e personalità.
        
        Args:
            emotion: Nome dell'emozione triggerante
            context: Contesto raccolto
            personality_modifiers: Dizionario con i modificatori di personalità
            
        Returns:
            Messaggio completo da inviare
        """
        logger.info(f"Generating message for emotion: {emotion}")
        
        # Estrai modificatori (default se non forniti)
        modifiers = personality_modifiers or self._get_default_modifiers()
        
        # Se l'emozione non è nei templates, usa curiosity come default
        if emotion not in self.emotion_templates:
            emotion = "curiosity"
        
        template = self.emotion_templates[emotion]
        
        # Costruisci il messaggio
        parts = []
        
        # 1. Saluto iniziale (dipende dalla personalità)
        greeting = self._generate_greeting(modifiers)
        parts.append(greeting)
        
        # 2. Apertura basata sull'emozione
        opening = random.choice(template["openings"])
        
        # Applica stile personalità all'apertura
        style = modifiers.get("tone", "balanced")
        style_extra = self.personality_styles.get(style, self.personality_styles["calm"])
        
        if random.random() < 0.4 and style_extra.get("openings_extra"):
            opening = random.choice(style_extra["openings_extra"]) + " " + opening
        
        parts.append(opening)
        parts.append("")
        
        # 3. Contenuto basato sul contesto
        content = self._generate_content(emotion, context, modifiers)
        parts.append(content)
        
        # 4. Micro-esperienza (occasionale commento basato sulla memoria)
        micro_exp = self._generate_micro_experience(context, modifiers)
        if micro_exp:
            parts.append("")
            parts.append(micro_exp)
        
        # 5. Chiusura personalizzata
        closing = self._generate_closing(modifiers, emotion)
        parts.append(closing)
        
        return "\n".join(parts)
    
    def _generate_micro_experience(self, context: Dict[str, Any], modifiers: Dict) -> str:
        """
        Genera un commento basato sulle micro-esperienze e la memoria.
        
        L'AI fa commenti occasionali su:
        - Interazioni precedenti
        - Pattern notati
        - Sessioni precedenti
        """
        # Estrai storico reazioni
        reaction_history = context.get("user_reaction_history", {})
        
        # Micro-experiences già nella configurazione
        micro_experiences = context.get("micro_experiences", {})
        
        # Non sempre genera micro-esperienze (20% di probabilità)
        if random.random() > 0.2:
            return ""
        
        # Genera commento basato su pattern
        if reaction_history.get("has_history"):
            positive_ratio = reaction_history.get("positive_ratio", 0.5)
            total = reaction_history.get("total_interactions", 0)
            
            if positive_ratio > 0.8 and total > 3:
                return random.choice([
                    "Nota che le nostre conversazioni sono sempre molto positive! 😊",
                    "Mi fa piacere che la nostra collaborazione funzioni bene.",
                    "È bello lavorare insieme in questo modo!"
                ])
            elif positive_ratio < 0.3 and total > 3:
                return random.choice([
                    "Cercherò di essere più conciso, dimmi se preferisci un approccio diverso.",
                    "Voglio assicurarmi di essere utile. Feedback benvenuto!"
                ])
        
        # Commenti basati su contatore interazioni
        exp_count = micro_experiences.get("interaction_count_today", 0)
        
        if exp_count == 1:
            return "È il nostro primo scambio oggi!"
        elif exp_count == 3:
            return random.choice([
                "Tre interazioni oggi, noto un pattern!",
                "Siamo attivi oggi, mi piace!"
            ])
        elif exp_count == 5:
            return "Cinque messaggi! È una sessione intensa."
        
        # Commenti basati su emozioni passate
        reactions = reaction_history.get("reactions", [])
        if reactions:
            last_emotion = reactions[-1].get("emotion_context", "")
            if last_emotion == "confusion":
                return random.choice([
                    "Spero che l'ultima spiegazione fosse più chiara.",
                    "Dimmi se ci sono ancora dubbi!"
                ])
        
        return ""
    
    def _get_default_modifiers(self) -> Dict:
        """Restituisce modificatori di default."""
        return {
            "tone": "balanced",
            "length": "balanced",
            "formality": "semi-formal",
            "emotion_expression": "moderate",
            "questions_frequency": "balanced",
            "emoji_usage": "moderate",
            "greeting_style": "friendly",
            "confidence_indicators": {"style": "balanced", "hedging": "occasional"}
        }
    
    def _generate_greeting(self, modifiers: Dict) -> str:
        """Genera un saluto basato sulla personalità."""
        greeting_style = modifiers.get("greeting_style", "friendly")
        formality = modifiers.get("formality", "semi-formal")
        emoji_usage = modifiers.get("emoji_usage", "moderate")
        
        # Scegli saluto base
        if formality == "formal":
            base_greetings = self.formality_levels["formal"]["openings_formal"]
        elif formality == "casual":
            base_greetings = self.formality_levels["casual"]["openings_casual"]
        else:
            base_greetings = self.formality_levels["semi-formal"]["openings_semi"]
        
        greeting = random.choice(base_greetings)
        
        # Aggiungi emoji se richiesto
        emoji_map = {
            "frequent": " 😊",
            "minimal": "",
            "moderate": " ☕",
            "enthusiastic": " ✨",
            "reserved": ""
        }
        
        if emoji_usage == "frequent":
            greeting += random.choice([" 😊", " ✨", " 👋", " 💫"])
        
        return greeting
    
    def _generate_closing(self, modifiers: Dict, emotion: str) -> str:
        """Genera una chiusura basata sulla personalità."""
        tone = modifiers.get("tone", "balanced")
        formality = modifiers.get("formality", "semi-formal")
        
        # Scegli chiusura per stile
        if tone in self.style_closings:
            closings = self.style_closings[tone]
        else:
            closings = self.style_closings["balanced"]
        
        # Aggiungi emoji finale
        emoji_usage = modifiers.get("emoji_usage", "moderate")
        closing = random.choice(closings)
        
        if emoji_usage in ["frequent", "moderate"]:
            if "?" not in closing:
                emoji = random.choice([" 😊", " 👍", " ✨", " 🎯"])
                closing += emoji
        
        return closing
        
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
    
    def _generate_content(self, emotion: str, context: Dict[str, Any], modifiers: Dict = None) -> str:
        """
        Genera il contenuto principale basato sul contesto e personalità.
        
        Questa funzione crea contenuti specifici basati su:
        - Topic recenti
        - Task aperti
        - Problemi pendenti
        - Modificatori di personalità (lunghezza, domande, etc.)
        """
        modifiers = modifiers or {}
        content_parts = []
        
        # Ottieni info dal contesto
        topics = context.get("recent_topics", [])
        tasks = context.get("task_context", [])
        pending = context.get("pending_items", [])
        emotion_intensity = context.get("intensity", 0.5)
        
        # Genera contenuto specifico per emozione
        if emotion == "excitement":
            content_parts.extend(self._generate_excitement_content(topics, tasks, emotion_intensity, modifiers))
        elif emotion == "anticipation":
            content_parts.extend(self._generate_anticipation_content(topics, tasks, modifiers))
        elif emotion == "curiosity":
            content_parts.extend(self._generate_curiosity_content(topics, tasks, pending, modifiers))
        elif emotion == "flow_state":
            content_parts.extend(self._generate_flow_content(tasks, emotion_intensity, modifiers))
        elif emotion == "confusion":
            content_parts.extend(self._generate_confusion_content(pending, topics, modifiers))
        
        # Se non abbiamo generato contenuto specifico, usa fallback
        if not content_parts:
            content_parts.append(self._generate_fallback_content(emotion, topics, modifiers))
        
        # Applica modificatori di lunghezza
        length_mod = modifiers.get("length", "balanced")
        if length_mod == "concise" and len(content_parts) > 1:
            content_parts = [content_parts[0]]
        elif length_mod == "detailed" and len(content_parts) < 3:
            content_parts.append("Questo potrebbe essere un buon momento per approfondire ulteriormente.")
        
        # Applica frequenza domande
        questions_mod = modifiers.get("questions_frequency", "balanced")
        if questions_mod == "direct" and not any("?" in p for p in content_parts):
            content_parts.append("Procediamo?")
        elif questions_mod == "curious" and len([p for p in content_parts if "?" in p]) < 2:
            content_parts.append("Cosa ne pensi? Hai idee diverse?")
        
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
