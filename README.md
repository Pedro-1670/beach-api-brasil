# 🌊 Beach API Brasil

API REST de condições climáticas das principais praias brasileiras, com dashboard visual em tempo real.

## ✨ Funcionalidades

- Consulta de clima, vento e ondas em tempo real
- Score de condição (0–100) calculado automaticamente
- Histórico salvo em banco de dados SQLite
- Ranking das melhores praias do dia
- Dashboard visual interativo

## 🚀 Como rodar localmente

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/beach-api-brasil
cd beach-api-brasil
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Rode a API
```bash
uvicorn main:app --reload
```

Acesse em: **http://localhost:8000**

Documentação automática: **http://localhost:8000/docs**

---

## 📡 Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/praias` | Lista todas as praias com condição atual |
| GET | `/praias/{nome}` | Dados de uma praia específica |
| GET | `/praias/{nome}/historico` | Histórico dos últimos N dias |
| GET | `/ranking` | Ranking das melhores praias do dia |

### Exemplos

```bash
# Todas as praias
curl http://localhost:8000/praias

# Praia específica
curl http://localhost:8000/praias/Santos

# Histórico dos últimos 7 dias
curl http://localhost:8000/praias/Ubatuba/historico?dias=7

# Ranking do dia
curl http://localhost:8000/ranking
```

---

## 🏖️ Praias disponíveis

| Praia | Estado |
|---|---|
| Santos | SP |
| Guarujá | SP |
| Ubatuba | SP |
| Florianópolis | SC |
| Balneário Camboriú | SC |
| Arraial do Cabo | RJ |
| Búzios | RJ |
| Porto Seguro | BA |
| Jericoacoara | CE |
| Maragogi | AL |

---

## 🧮 Como o score é calculado

O score (0–100) leva em conta:

- **Altura das ondas**: ideal entre 0.5m e 1.5m
- **Velocidade do vento**: quanto menor, melhor
- **Temperatura**: ideal entre 24°C e 32°C

| Score | Condição |
|---|---|
| 80–100 | Excelente ✅ |
| 60–79 | Boa 🟡 |
| 40–59 | Regular 🟠 |
| 0–39 | Ruim ❌ |

---

## 🛠️ Stack

- **Backend**: Python + FastAPI
- **Banco de dados**: SQLite
- **Dados climáticos**: [Open-Meteo API](https://open-meteo.com/) (gratuita, sem key)
- **Frontend**: HTML + CSS + JavaScript vanilla

## ☁️ Deploy gratuito

Recomendado: [Railway](https://railway.app) ou [Render](https://render.com)

---

Feito com 🌊 por Pedro Ryan
