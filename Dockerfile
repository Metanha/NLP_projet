# Utiliser une image Python officielle comme base
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# 📥 3. Copier les fichiers du projet
COPY . /app


# Copier les fichiers nécessaires
COPY requirements.txt .
#COPY Projet_polerisation1.ipynb .

# Installer les dépendances
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download fr_core_news_md

# Installer Jupyter
#RUN pip install jupyter

# Exposer le port pour Jupyter
EXPOSE 8888

# Commande pour lancer Jupyter
CMD ["streamlit", "run", "app.py", "--server.port=8888", "--server.address=0.0.0.0"]