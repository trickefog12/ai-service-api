# Χρησιμοποιούμε μια ελαφριά έκδοση της Python 3.11
FROM python:3.11-slim

# Ορίζουμε το φάκελο εργασίας μέσα στο container
WORKDIR /app

# Αντιγράφουμε πρώτα το requirements.txt για να εκμεταλλευτούμε το Docker cache
COPY requirements.txt .

# Εγκατάσταση των βιβλιοθηκών
RUN pip install --no-cache-dir -r requirements.txt

# Αντιγράφουμε τον υπόλοιπο κώδικα
COPY . .

# Ορίζουμε την πόρτα που ακούει το Cloud Run (default 8080)
ENV PORT=8080

# Εντολή για την εκκίνηση του API
# Χρησιμοποιούμε το 0.0.0.0 για να δέχεται κίνηση από το δίκτυο του Cloud Run
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]