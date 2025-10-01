import re
import random
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.corpus import stopwords

try:
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

def simplify_sentence(sentence):
    """Simplify a sentence by removing complex clauses and making it more direct"""
    simplified = re.sub(r'[,;].*?(?=\.|$)', '', sentence)
    simplified = re.sub(r'\(.*?\)', '', simplified)
    simplified = re.sub(r'\b(however|although|despite|nevertheless|furthermore|moreover)\b', '', simplified, flags=re.IGNORECASE)
    
    simplified = re.sub(r'\b(is|are|was|were)\s+able to\b', 'can', simplified, flags=re.IGNORECASE)
    simplified = re.sub(r'\b(utilize|utilizes|utilized)\b', 'use', simplified, flags=re.IGNORECASE)
    simplified = re.sub(r'\b(approximately|roughly|about)\b', '~', simplified, flags=re.IGNORECASE)
    
    simplified = re.sub(r'\s+', ' ', simplified).strip()
    
    return simplified

def extract_key_concepts(text):
    """Extract important concepts from text"""
    try:
        words = word_tokenize(text)
        tagged = pos_tag(words)
        stop_words = set(stopwords.words('english'))
        concepts = [word for word, pos in tagged if pos in ['NN', 'NNS', 'NNP', 'NNPS'] 
                   and word.lower() not in stop_words and len(word) > 3]
        return list(set(concepts))[:8]
    except:
        words = re.findall(r'\b[A-Z][a-z]+\b', text)
        common_words = ['the', 'and', 'is', 'in', 'of', 'to', 'a', 'that', 'it', 'with', 'for', 'as', 'was', 'on']
        concepts = [word for word in words if word.lower() not in common_words and len(word) > 3]
        return list(set(concepts))[:8]

def identify_main_points(text, num_points=5):
    """Identify and extract main points from text with proper scoring"""
    text = re.sub(r'\s+', ' ', text).strip()
    
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if len(s.strip()) > 10]
    
    if len(sentences) <= num_points:
        return [simplify_sentence(s) for s in sentences]
    
    key_concepts = extract_key_concepts(text)
    
    scored_sentences = []
    for sentence in sentences:
        score = 0
        
        position = sentences.index(sentence)
        if position == 0:
            score += 3
        elif position < 3:
            score += 2
        elif position == len(sentences) - 1:
            score += 2
        
        sentence_words = set(word.lower() for word in word_tokenize(sentence))
        for concept in key_concepts:
            if concept.lower() in sentence_words:
                score += 2
        
        word_count = len(sentence.split())
        if 8 <= word_count <= 20:
            score += 1
        
        importance_indicators = ['important', 'key', 'main', 'primary', 'essential', 'critical', 'significant', 'fundamental']
        if any(indicator in sentence.lower() for indicator in importance_indicators):
            score += 3
        
        scored_sentences.append((score, sentence))
    
    scored_sentences.sort(reverse=True)
    top_sentences = [sentence for score, sentence in scored_sentences[:num_points]]
    
    simplified_points = []
    for sentence in top_sentences:
        simplified = simplify_sentence(sentence)
        if len(simplified.split()) >= 4:
            simplified = simplified[0].upper() + simplified[1:] if simplified else ""
            simplified_points.append(simplified)
    
    return simplified_points[:num_points]

def generate_smart_summary(text, num_points=5):
    """Generate a proper summary with main points in simple language"""
    main_points = identify_main_points(text, num_points)
    
    if not main_points or len(main_points) < 2:
        return create_basic_summary(text, num_points)
    
    return main_points

def create_basic_summary(text, num_points=5):
    """Create basic summary points when automatic extraction fails"""
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if len(s.strip()) > 20]
    
    if len(sentences) <= num_points:
        return [s for s in sentences[:num_points]]
    
    points = []
    if sentences:
        points.append(sentences[0])
    if len(sentences) > 2:
        points.append(sentences[len(sentences)//2])
    if len(sentences) > 1:
        points.append(sentences[-1])
    
    remaining = num_points - len(points)
    if remaining > 0:
        for i in range(1, min(remaining + 1, len(sentences) - 1)):
            if sentences[i] not in points:
                points.append(sentences[i])
    
    return [simplify_sentence(p) for p in points[:num_points]]

def get_study_tips():
    return [
        "Break complex topics into smaller, manageable chunks for better understanding.",
        "Use spaced repetition to reinforce learning over time.",
        "Create mind maps to visualize connections between concepts.",
        "Teach what you've learned to someone else to solidify your understanding.",
        "Practice active recall by testing yourself without looking at notes.",
        "Connect new information to what you already know for better retention.",
        "Take regular breaks to maintain focus and prevent burnout.",
        "Use multiple senses (read, write, speak) to engage different learning pathways.",
        "Set specific, measurable goals for each study session.",
        "Review material within 24 hours to move it from short-term to long-term memory."
    ]