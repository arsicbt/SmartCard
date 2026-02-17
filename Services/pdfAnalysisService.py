"""
pdfAnalysisService.py - Service d'analyse de PDF avec Groq

Ce service gère :
1. Extraction du texte depuis un PDF
2. Analyse du contenu par Groq pour déduire le thème
3. Génération de questions/réponses basées sur le PDF
4. Transformation en Quiz ou Cards selon le type de session
"""

import os
import re
from typing import Dict, List, Optional, Tuple
import PyPDF2
import json
from groq import Groq
from io import BytesIO
from dotenv import load_dotenv

load_dotenv() 

# Configuration Groq
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    raise ValueError("Groq à besoin de sa clé dans les var d'environement")

groq_client = Groq(api_key=GROQ_API_KEY)


class PDFAnalysisService:
    """Service pour analyser des PDFs et générer du contenu éducatif"""
    
    # ********************************************************
    # EXTRACTION DE TEXTE
    # ********************************************************
    
    @staticmethod
    def extract_text_from_pdf(pdf_file) -> str:
        """
        Extrait le texte d'un fichier PDF
        
        Args:
            pdf_file: Fichier PDF (FileStorage Flask ou BytesIO)
        
        Returns:
            Texte extrait du PDF
        
        Raises:
            ValueError: Si le PDF est invalide ou vide
        """
        try:
            # Convertir en BytesIO si nécessaire
            if hasattr(pdf_file, 'read'):
                pdf_bytes = BytesIO(pdf_file.read())
            else:
                pdf_bytes = pdf_file
            
            # Lire le PDF
            pdf_reader = PyPDF2.PdfReader(pdf_bytes)
            
            if len(pdf_reader.pages) == 0:
                raise ValueError("PDF is empty")
            
            # Extraire le texte de toutes les pages
            text_content = []
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
                    
            full_text = "\n\n".join(text_content)
            
            if not full_text.strip():
                raise ValueError("No text could be extracted from PDF")
            
            return full_text.strip()
            
        except Execption as e:
            raise ValueError(f"Error extracting PDF text: {str(e)}")
        
        
    # ********************************************************
    # ANALYSE DU THÈME PAR GROQ
    # ********************************************************
    
    @staticmethod
    def analyse_theme_with_groq(pdf_content: str) -> Dict[str, any]:
        """
        Analyse le contenu du PDF avec Groq pour déduire le thème
        
        Args:
            pdf_content: Contenu textuel du PDF
        
        Returns:
            Dict avec:
                - theme_name: Nom du thème déduit
                - keywords: Liste de mots-clés (max 10)
                - description: Description courte du thème
        
        Example:
            {
                "theme_name": "Python Programming Basics",
                "keywords": ["python", "variables", "functions", "loops", "OOP"],
                "description": "Introduction to Python programming fundamentals"
            }
        """
        
        # limiter le contenue à 4000 caractere pour le MVP
        content_sample = pdf_content[:4000] if len(pdf_content) > 4000 else pdf_content
        
        prompt = f"""Analyze the following educational content and extract the main theme.

CONTENT:
{content_sample}

Your task:
1. Identify the MAIN THEME (subject/topic) of this content
2. Extract 5-10 KEYWORDS that best represent this theme
3. Write a SHORT DESCRIPTION (max 200 characters)

Respond ONLY with valid JSON in this exact format:
{{
    "theme_name": "Main Theme Name",
    "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
    "description": "Brief description of the theme"
}}

Important:
- Theme name should be concise (2-5 words)
- Keywords should be lowercase, single words or short phrases
- Description should be one sentence
- Return ONLY the JSON, no other text"""

        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educator who creates high-quality study materials. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            # Extraire la réponse
            result_text = response.choices[0].message.content.strip()
            
            # Nettoyer la réponse
            result_text = re.sub(r'```json\s*', '', result_text)
            result_text = re.sub(r'```\s*', '', result_text)
            
            # Parser le JSON
            questions_data = json.loads(result_text)
            
            # Valider
            if 'questions' not in questions_data or not isinstance(questions_data['questions'], list):
                raise ValueError("Invalid questions structure")
            
            return questions_data['questions']
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse Groq response as JSON: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error generating questions with Groq: {str(e)}")
    
        
    # ********************************************************
    # GÉNÉRATION DE QUESTIONS/RÉPONSES
    # ********************************************************
    
    @staticmethod
    def generate_questions_from_pdf(
        pdf_content: str,
        session_type: str,
        count: int = 10
    ) -> List[Dict[str, any]]:
        """
        Génère des questions à partir du contenu PDF
        
        Args:
            pdf_content: Contenu du PDF
            session_type: "QUIZ" ou "FLASHCARD"
            count: Nombre de questions à générer (défaut 10)
        
        Returns:
            Liste de questions avec leurs réponses
            
        Format QUIZ:
        [
            {
                "question": "What is Python?",
                "answers": [
                    {"text": "A programming language", "is_correct": true},
                    {"text": "A snake", "is_correct": false},
                    {"text": "A framework", "is_correct": false},
                    {"text": "A database", "is_correct": false}
                ],
                "explanation": "Python is a high-level programming language",
                "difficulty": "EASY"
            }
        ]
        
        Format FLASHCARD:
        [
            {
                "question": "What is a variable in Python?",
                "answer": "A variable is a container for storing data values",
                "difficulty": "EASY"
            }
        ]
        """
        # Limiter le contenu
        content_sample = pdf_content[:6000] if len(pdf_content) > 6000 else pdf_content
        
        if session_type == "QUIZ":
            prompt = f"""Based on the following educational content, generate {count} multiple-choice quiz questions.

CONTENT:
{content_sample}

Generate {count} quiz questions with 4 answer options each (1 correct, 3 incorrect).

Respond ONLY with valid JSON in this exact format:
{{
    "questions": [
        {{
            "question": "Question text here?",
            "answers": [
                {{"text": "Correct answer", "is_correct": true}},
                {{"text": "Wrong answer 1", "is_correct": false}},
                {{"text": "Wrong answer 2", "is_correct": false}},
                {{"text": "Wrong answer 3", "is_correct": false}}
            ],
            "explanation": "Brief explanation of why the correct answer is correct",
            "difficulty": "EASY"
        }}
    ]
}}

Requirements:
- Mix difficulty levels: EASY, MEDIUM, HARD
- Questions should test understanding, not just memorization
- Make wrong answers plausible but clearly incorrect
- Explanations should be 1-2 sentences
- Return ONLY the JSON, no other text"""
        
        else:  # FLASHCARD
            prompt = f"""Based on the following educational content, generate {count} flashcard-style questions.

CONTENT:
{content_sample}

Generate {count} flashcard questions (question on front, answer on back).

Respond ONLY with valid JSON in this exact format:
{{
    "questions": [
        {{
            "question": "Question or term to remember?",
            "answer": "Complete answer or definition",
            "difficulty": "EASY"
        }}
    ]
}}

Requirements:
- Mix difficulty levels: EASY, MEDIUM, HARD
- Questions should be clear and specific
- Answers should be concise but complete (2-4 sentences max)
- Return ONLY the JSON, no other text"""
        
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educator who creates high-quality study materials. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            # Extraire la réponse
            result_text = response.choices[0].message.content.strip()
            
            # Nettoyer la réponse
            result_text = re.sub(r'```json\s*', '', result_text)
            result_text = re.sub(r'```\s*', '', result_text)
            
            # Parser le JSON
            questions_data = json.loads(result_text)
            
            # Valider
            if 'questions' not in questions_data or not isinstance(questions_data['questions'], list):
                raise ValueError("Invalid questions structure")
            
            return questions_data['questions']
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse Groq response as JSON: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error generating questions with Groq: {str(e)}")
    

    # ********************************************************
    # PIPELINE COMPLET
    # ********************************************************
    
    @staticmethod
    def analysis_pdf_fulll_pipeline(
        pdf_file,
        session_type: str,
        questions_count: int = 10
    ) -> Dict[str, any]:
        """
        Pipeline complet d'analyse PDF
        
        Args:
            pdf_file: Fichier PDF
            session_type: "QUIZ" ou "FLASHCARD"
            questions_count: Nombre de questions à générer
        
        Returns:
            Dict contenant:
                - pdf_content: Contenu textuel extrait
                - theme: Données du thème (name, keywords, description)
                - questions: Liste des questions générées
        """
        # Etape 1: Extraire le texte
        pdf_content = PDFAnalysisService.extract_text_from_pdf(pdf_file)
        
        # Etape 2: Analyser le theme
        theme_data = PDFAnalysisService.analyze_theme_with_groq(pdf_content)
        
        # Etape 3: Générer les questions
        questions = PDFAnalysisService.generate_questions_from_pdf(
            pdf_content,
            session_type,
            questions_count
        )
        
        return {
            'pdf_content': pddf_content,
            'theme': theme_data,
            'questions': questions
        }
