Crea environment
Installa requirements
Esegui con

    streamlit run fe.py

e conversa.

Creazione DB: 

```
docker run -e POSTGRES_USER=myuser \
           -e POSTGRES_PASSWORD=mypassword \
           -e POSTGRES_DB=mydatabase \
           --name my_postgres \
           -p 5432:5432 \
           -d pgvector/pgvector:0.8.0-pg17
```