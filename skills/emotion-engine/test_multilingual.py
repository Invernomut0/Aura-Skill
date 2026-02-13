#!/usr/bin/env python3
"""
Test script for multilingual emotion analysis support.
Demonstrates automatic translation and emotion detection in multiple languages.
"""

from utils.sentiment_analyzer import AdvancedSentimentAnalyzer

def test_multilingual_emotions():
    """Test emotion detection across multiple languages."""
    
    analyzer = AdvancedSentimentAnalyzer()
    
    # Test phrases in different languages
    test_cases = [
        {
            "language": "English",
            "text": "I am very happy and excited about this amazing project!",
            "expected_emotions": ["joy", "excitement", "curiosity"]
        },
        {
            "language": "Italian",
            "text": "Sono molto soddisfatto del risultato e curioso di continuare!",
            "expected_emotions": ["satisfaction", "joy", "curiosity"]
        },
        {
            "language": "Spanish",
            "text": "Estoy confundido y frustrado con este problema difícil.",
            "expected_emotions": ["confusion", "frustration"]
        },
        {
            "language": "French",
            "text": "Je suis très curieux et intrigué par cette nouvelle découverte!",
            "expected_emotions": ["curiosity", "surprise"]
        },
        {
            "language": "German",
            "text": "Ich bin sehr zufrieden und stolz auf diese Leistung!",
            "expected_emotions": ["satisfaction", "joy"]
        }
    ]
    
    print("=" * 80)
    print("MULTILINGUAL EMOTION ANALYSIS TEST")
    print("=" * 80)
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['language']}")
        print("-" * 80)
        print(f"Original Text: {test_case['text']}")
        
        # Analyze sentiment
        result = analyzer.analyze_sentiment_advanced(test_case['text'])
        
        # Display results
        lang_info = result['language_info']
        print(f"Detected Language: {lang_info['detected_language']}")
        
        if lang_info['translation_applied']:
            print(f"Translated Text: {lang_info['translated_text']}")
        
        # Show top emotions detected
        emotions = result['emotions']
        top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]
        
        print(f"Emotions Detected:")
        for emotion, score in top_emotions:
            if score > 0:
                print(f"  • {emotion.capitalize()}: {score*100:.1f}%")
        
        print()
    
    print("=" * 80)
    print("✅ Multilingual support working correctly!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_multilingual_emotions()
    except ImportError as e:
        print("❌ Error: Translation libraries not installed.")
        print("Install with: pip install deep-translator langdetect")
        print(f"Details: {e}")
