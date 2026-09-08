# Jarvis Backend

Backend FastAPI que tira a API key da Anthropic do navegador e coloca as notas
do Second Brain num Postgres (Supabase) — acessível de qualquer navegador/dispositivo.

## 1. Criar o banco (Supabase, grátis)

1. Crie um projeto em https://supabase.com
2. Vá em **SQL Editor** → cole o conteúdo de `schema.sql` → Run
   (isso cria as tabelas `notes` e `relations` já com as 24 notas iniciais)
3. Vá em **Settings → Database → Connection string** → copie a URI (modo *Session pooler*)

## 2. Configurar o backend

```bash
cd jarvis-backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edite o `.env`:
- `DATABASE_URL` → a connection string do Supabase
- `ANTHROPIC_API_KEY` → sua chave em console.anthropic.com
- `CORS_ORIGINS` → em dev pode deixar `*`; em produção, coloque o domínio do frontend

## 3. Rodar local

```bash
uvicorn main:app --reload
```

Abre em `http://localhost:8000`. Documentação automática em `http://localhost:8000/docs`.

## 4. Testar rápido

```bash
curl http://localhost:8000/notes
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Fala Jarvis, como estão minhas metas?","history":[]}'
```

## 5. Deploy (Railway, grátis pra começar)

1. Suba esta pasta num repositório GitHub
2. Em railway.app → New Project → Deploy from GitHub
3. Configure as mesmas variáveis de ambiente do `.env`
4. Railway detecta o `requirements.txt` e builda sozinho — só ajuste o Start Command:
   `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Pegue a URL pública gerada (ex: `https://jarvis-backend-production.up.railway.app`)

## 6. Ajustar o frontend (`jarvis.html`)

Troque:
- o campo de API key na UI → remova (não é mais necessário no client)
- a chamada direta à Anthropic em `processCommand()` → troque por:

```js
const res = await fetch("https://SEU-BACKEND.up.railway.app/chat", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ message: text, history: sessionHistory })
});
const data = await res.json();
// data.reply já vem limpo (sem [[SAVE:...]]), e data.saved_note indica se algo foi salvo
```

- as chamadas de CRUD de notas (`localStorage`) → trocam por `GET/POST/PUT/DELETE` em `/notes`
  e `GET /relations` pra carregar o grafo.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/notes` | lista todas as notas |
| POST | `/notes` | cria nota `{area, title, body}` |
| PUT | `/notes/{id}` | atualiza nota |
| DELETE | `/notes/{id}` | remove nota (e relações ligadas) |
| GET | `/relations` | lista conexões do grafo |
| POST | `/chat` | `{message, history}` → chama Claude com o Second Brain injetado, trata `[[SAVE:...]]` e grava no banco |
| GET | `/health` | healthcheck |
