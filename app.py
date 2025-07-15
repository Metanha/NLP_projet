# 📦 Chargement des objets sauvegardés
import streamlit as st
import joblib
import re
import spacy
import random
from datetime import datetime
import unicodedata
import emoji
from typing import Union, List

# --- CONFIG PAGE ---
# Page Streamlit
st.set_page_config(page_title="Correcteur Grammatical", page_icon="📘", layout="centered")


st.sidebar.title("🎨 Thème")
theme = st.sidebar.selectbox("Choisissez un thème :", ["Clair", "Bleu", "Beige"])

if theme == "Clair":
    css = """
    <style>
        [data-testid="stAppViewContainer"] {
            background-color: #ffffff;
        }
        .stTextArea textarea {
            background-color: #f3f3f3;
        }
        .result-box {
            background-color: #e8fce8;
            border-left: 6px solid #4caf50;
        }
    </style>
    """
elif theme == "Bleu":
    css = """
    <style>
        [data-testid="stAppViewContainer"] {
            background-color: #f0f8ff;
        }
        .stTextArea textarea {
            background-color: #e8f0fa;
        }
        .result-box {
            background-color: #e3f2fd;
            border-left: 6px solid #1565c0;
        }
    </style>
    """
elif theme == "Beige":
    css = """
    <style>
        [data-testid="stAppViewContainer"] {
            background-color: #fffaf0;
        }
        .stTextArea textarea {
            background-color: #fff5e6;
        }
        .result-box {
            background-color: #fef2dc;
            border-left: 6px solid #8d6e63;
        }
    </style>
    """
st.markdown(css, unsafe_allow_html=True)
# Appliquer le CSS
#st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Titre dynamique avec date formatée en français
jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
mois = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
today = datetime.today()
date_str = f"{jours[today.weekday()]} {today.day} {mois[today.month - 1]} {today.year}"


# --- CSS personnalisé ---
st.markdown("""
    <style>

        .stTextArea textarea {
            background-color: #fff9e6;
            border-radius: 6px;
        }
        .stButton button {
            background-color: #6d4c41;
            color: white;
            font-weight: bold;
            border-radius: 8px;
        }
        .stButton button:hover {
            background-color: #4e342e;
        }
        .result-box {
            background-color: #e9fce9;
            border-left: 6px solid #2e7d32;
            padding: 16px;
            border-radius: 6px;
        }
    </style>
""", unsafe_allow_html=True)


model = joblib.load("modele_regression_logistique.joblib")
vectorizer = joblib.load("vectoriseur_tfidf_1000.joblib")
nlp = spacy.load("fr_core_news_md")

# 🧽 Fonction de nettoyage
@st.cache_data #Il cache les résultats de vos fonctions pour éviter des recalculs inutiles
def nettoyer_texte(texte:str):

    # 1. Nettoyage initial
    texte = re.sub(r'<[^>]+>', '', texte)
    texte = emoji.demojize(texte, language='fr')
    
    # 2. Lemmatisation
    doc = nlp(texte)
    lemmes = [token.lemma_ for token in doc]
    
    # 3. Nettoyage supplémentaire
    texte = ' '.join(lemmes).lower()
    texte = re.sub(r'[^\w\s\'-]', '', texte)
    texte = re.sub(r'\d+', '', texte)
    texte = unicodedata.normalize('NFKD', texte).encode('ascii', 'ignore').decode('utf-8')
    texte = re.sub(r'\s+', ' ', texte).strip()
    
    # 4. Tokenisation et filtrage
    doc = nlp(texte)
    stop_words = nlp.Defaults.stop_words
    punctuation = set(spacy.lang.punctuation.TOKENIZER_PREFIXES + 
                     spacy.lang.punctuation.TOKENIZER_SUFFIXES + 
                     spacy.lang.punctuation.TOKENIZER_INFIXES)
    
    final_tokens = [
        token.text.lower()
        for token in doc
        if (token.text.lower() not in stop_words and
            token.text not in punctuation and
            token.text.strip() not in ['-', ''] and 
            len(token.text) >= 2)
    ]
    
    return ' '.join(final_tokens)



# 🖼️ Interface utilisateur
st.title("🗣️ Classification d'avis client")
st.markdown("Détermine si un avis est **positif** ou **négatif**")

# Zone de saisie
avis = st.text_area("✍️ Saisis un avis client ici :",
                    placeholder="Tapez votre avis ici...")

if st.button("Analyser"):
    if avis.strip(" ")=="":
        st.error("Aucun avis saisi, saisez un avis")
    else:
        avis_clean = nettoyer_texte(avis)
        if avis_clean=="" or None or len(avis)==0:
          st.error("Avis saisit non valide")  
        else:
            vecteur = vectorizer.transform([avis_clean])
            prediction = model.predict(vecteur)[0]
            # Affichage résultat
            if prediction == 1:
                st.success("✅ Avis **positif** détecté.")
            else:
                st.error("❌ Avis **négatif** détecté.")
