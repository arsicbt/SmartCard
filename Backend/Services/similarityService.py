"""
similarityService.py - Service de calcul de similarité entre contenus

Ce service calcule la correspondance entre :
- Le contenu d'un PDF et des questions existantes
- Des mots-clés et des thèmes existants

Utilise une approche simple mais efficace basée sur :
1. TF-IDF pour extraire les mots importants
2. Intersection de sets pour calculer la similarité
"""


from typing import List, Set, Dict
import re
from collections import Counter
import math


class SimilarityService:
    """Service pour calculer la similarité entre textes et questions"""
    
    # Indicateur qu'il va y avoir un mot à traiter (francais/anglais)
    STOP_WORDS = {
        # Français
        'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'ou', 'mais',
        'donc', 'or', 'ni', 'car', 'ce', 'ces', 'mon', 'ton', 'son', 'ma', 'ta',
        'sa', 'mes', 'tes', 'ses', 'notre', 'votre', 'leur', 'nos', 'vos', 'leurs',
        'qui', 'que', 'quoi', 'dont', 'où', 'dans', 'sur', 'sous', 'avec', 'sans',
        'pour', 'par', 'est', 'sont', 'être', 'avoir', 'il', 'elle', 'on', 'nous',
        'vous', 'ils', 'elles', 'je', 'tu', 'à', 'au', 'aux', 'en', 'y', 'plus',
        # Anglais
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'should', 'could', 'may', 'might', 'must', 'can', 'it', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'we', 'they', 'what', 'which',
        'who', 'when', 'where', 'why', 'how'
    }
    
    
    # ********************************************************
    # PREPROCESSING
    # ********************************************************
    
    @staticmethod
    def preprocess_text(text:str) -> List[str]:
        """
        Prétraite un texte : lowercase, tokenize, remove stop words
        
        Args:
            text: Texte à traiter
        
        Returns:
            Liste de mots pertinents
        """
        
        # Lowercase
        text = text.lower()
        
        # Garder uniquement les lettres, chiffres et espaces 
        text = re.sub(r'[^a-zà-ÿ0-9\s]', ' ', text)
        
        # Tokenize
        words = text.split()
        
        # Filtrer les stops words et mots trop coruts
        word = [
                w for w in words
                if w not in SimilarityService.STOP_WORDS and len(w) > 2
                ]
        
        return words
    
    
    @staticmethod
    def extact_keywords(text: str, top_n: int = 20) -> List[str]:
        """
        Extrait les mots-clés les plus importants d'un texte
        
        Utilise la fréquence des mots comme métrique simple
        
        Args:
            text: Texte source
            top_n: Nombre de mots-clés à extraire
        
        Returns:
            Liste des top_n mots-clés
        """
        words = SimilarityService.preprocess_text(text)
        
        if not words:
            return []
        
        # Compter les fréquences
        word_counts = Counter(words)
        
        # Prendre les top_n plus fréquents 
        top_words = words_counts.most_common(top_n)
        
        return [word for word, count in top_words]
    
    
    # ********************************************************
    # CALCUL DE SIMILARITÉ
    # ********************************************************
    
    @staticmethod
    def calcullate_text_similarity(text1: str, text2: str) -> float:
        """
        Calcule la similarité entre deux textes
        
        Utilise le coefficient de Jaccard sur les mots-clés
        
        Args:
            text1: Premier texte
            text2: Deuxième texte
        
        Returns:
            Score de similarité entre 0.0 et 1.0
            
        Formula:
            Jaccard = |A ∩ B| / |A ∪ B|
        """
        
        # Extraire les mots_clés 
        keywords1 = set(SimilarityService.extract_keywords(text1, top_n=30))
        keywords2 = set(SimilarityService.extract_keywords(text2, top_n=30))
        
        if not keywords1 or not keywords2:
            return 0.0
        
        # Intersection et union
        intersection = keywords1 & keywords2
        union = keywords1 | keywords2
        
        # Coefficient de Jaccard
        if len(union) == 0:
            return 0.0
        
        similarity = len(intersection) / len(union)
        
        return similarity
        
    
    @staticmethod
    def calculate_keyword_ooverlap(
        text_keywords: List[str],
        target_keywords: List[str]
    ) -> float:
        """
        Calcule le chevauchement entre deux listes de mots-clés
        
        Args:
            text_keywords: Mots-clés du texte source
            target_keywords: Mots-clés cibles
        
        Returns:
            Score entre 0.0 et 1.0
        """
        if not text_keywords or not target_keywords:
            return 0.0
        
        set1 = set(k.lower().strip() for k in text_keywords)
        set2 = set(k.lower().strip() for k in target_keywords)
        
        intersection = set1 & set2
        
        # Calculer par rapport à la taille du plus petit set
        min_size = min(len(set1), len(set2))
        
        if min_size == 0:
            return 0.0
        
        return len(intersection) / min_size
    

    # ********************************************************
    # MATCHING AVEC QUESTIONS
    # ********************************************************
    
    @staticmethod
    def find_matching_questions(
        pdf_content: str,
        questions: List[Dict],
        threshold: float = 0.4
    ) -> List[Dict]:
        """
        Trouve les questions qui correspondent au contenu du PDF
        
        Args:
            pdf_content: Contenu du PDF
            questions: Liste de questions (dict avec 'question_text' et 'id')
            threshold: Seuil minimum de similarité (0.4 = 40%)
        
        Returns:
            Liste de questions avec leur score de similarité
            Format: [
                {
                    'question': question_dict,
                    'similarity_score': 0.67
                },
                ...
            ]
        """
        # Extraire les mots-clés du PDF
        pdf_keywords = SimilarityService.extract_keywords(pdf_content, top_n=50)
        
        matching_questions = []
        
        for question in questions:
            # Texte de la question
            question_text = question.get('question_text', '')
            
            # Calculer la similarité
            similarity = SimilarityService.calculate_text_similarity(
                pdf_content,
                question_text
            )
            
            # Si au-dessus du seuil, ajouter
            if similarity >= threshold:
                matching_questions.append({
                    'question': question,
                    'similarity_score': similarity
                })
        
        # Trier par score décroissant
        matching_questions.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return matching_questions
        

    # ********************************************************
    # MATCHING AVEC THÈMES
    # ********************************************************
    
    @staticmethod
    def find_matching_theme(
        pdf_keywords: List[str],
        themes: List[Dict],
        threshold: float = 0.4
    ) -> Dict:
        """
        Trouve le thème qui correspond le mieux aux mots-clés du PDF
        
        Args:
            pdf_keywords: Mots-clés extraits du PDF
            themes: Liste de thèmes (dict avec 'id', 'name', 'keywords')
            threshold: Seuil minimum de correspondance (0.4 = 40%)
        
        Returns:
            Meilleur thème correspondant ou None
            Format: {
                'theme': theme_dict,
                'match_score': 0.65
            }
        """
        best_match = None
        best_score = 0.0
        
        for theme in themes:
            theme_keywords = theme.get('keywords', [])
            
            # Calculer le chevauchement
            overlap = SimilarityService.calculate_keyword_overlap(
                pdf_keywords,
                theme_keywords
            )
            
            # Mettre à jour si meilleur score
            if overlap >= threshold and overlap > best_score:
                best_score = overlap
                best_match = {
                    'theme': theme,
                    'match_score': overlap
                }
        
        return best_match
