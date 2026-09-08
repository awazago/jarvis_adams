# Jarvis Adams

Assistente de voz pessoal com Second Brain — frontend em HTML puro + backend
FastAPI/Postgres.

## Estrutura

```
jarvis_adams/
├── frontend/
│   └── jarvis.html      → abra direto no navegador (Chrome recomendado)
└── backend/
    ├── main.py          → API FastAPI (/notes, /relations, /chat)
    ├── ...
    └── README.md        → setup detalhado do backend (Supabase + deploy)
```

## Como rodar

1. Suba o backend primeiro — siga `backend/README.md` (Supabase + FastAPI local ou Railway).
2. No `frontend/jarvis.html`, ajuste a constante `BACKEND_URL` no topo do `<script>`
   para a URL do backend (local `http://localhost:8000` ou a URL do Railway após deploy).
3. Abra o `frontend/jarvis.html` no navegador, clique em **ATIVAR SISTEMA**,
   permita o microfone e diga **"fala jarvis"**.

A chave da Anthropic fica só no backend (`.env`), nunca no navegador.
