# Counter-Strike — predição de kill (Big Data / Spark)

Projeto de Big Data: ambiente **Apache Spark** + **Jupyter (PySpark)** em **Docker** para EDA e modelagem sobre dados de Counter-Strike.

## Parte 1 — Ambiente (Spark + Docker)

### Pré-requisitos

- **WSL2** (Ubuntu ou outra distro) com o repositório clonado no **diretório Linux** (ex.: `~/projetos/...`), não em `/mnt/c/...` se possível — melhor desempenho e menos problemas com o Docker.
- [Docker](https://docs.docker.com/engine/install/) instalado (Docker Desktop usando o *backend* WSL2 ou o *daemon* no Linux do WSL).

### Estrutura

| Caminho | Uso |
|--------|-----|
| `data/` | Dataset Parquet (não versionado; ver `.gitignore`) |
| `src/` | Scripts, ex.: `data_extract.py` |
| `notebooks/` | Jupyter (EDA, modelos) |
| `docker-compose.yml` | Sobe o **jupyter/pyspark-notebook** (alinhado ao comando do professor) |

### Subir o ambiente

Na raiz do repositório (no WSL):

```bash
cp .env.example .env
docker compose up -d
```

- **Jupyter:** [http://localhost:8888](http://localhost:8888) (porta ajustável em `JUPYTER_PORT` no arquivo `.env`).
- **Token de acesso:** `docker logs spark-container 2>&1 | head -n 30` — procura por `http://127.0.0.1:8888/lab?token=...` ou `token=`.

Para parar:

```bash
docker compose down
```

### Onde fica o `work` do container

O projeto na máquina host é montado em `/home/jovyan/work` dentro do container. No notebook, arquivos na raiz do repositório são acessíveis com caminhos relativos a partir de `/home/jovyan/work` (p.ex. abrir o notebook a partir de `work/notebooks/`).

Dataset gerado: **`data/csgo_full_dataset.parquet`**. No PySpark, por exemplo:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("csgo-eda").getOrCreate()
df = spark.read.parquet("data/csgo_full_dataset.parquet")
```

### Portas

| Porta | Uso |
|-------|-----|
| 8888 | Jupyter (ou valor de `JUPYTER_PORT`) |
| 4040 | *Spark UI* do job ativo (quando um job estiver a correr) |
| 7077 | Reservada a cenários *standalone*; no modo `local` típico pode não ter serviço a escutar. |

### Memória (máquinas com ~8 GB de RAM)

O `docker-compose` limita o serviço a **5G** de RAM para não derrubar o host. Se precisar de mais, edita `mem_limit` / `memswap_limit` consoante a tua máquina.

No notebook, em máquinas lentas, pode-se restringir o *local* do Spark, por exemplo `SparkSession.builder.config("spark.default.parallelism", "2")` ou `.master("local[2]")` conforme a API que for usada (ajusta conforme o código da célula).

### Equivalência ao `docker` do professor

```bash
docker run --name spark-container -p 8888:8888 -p 4040:4040 -p 7077:7077 \
  -v "$(pwd)":/home/jovyan/work jupyter/pyspark-notebook
```

O `docker compose` acima é a mesma ideia, com nome de serviço e limites de memória para a equipa.

### Gerar o Parquet (quando tiveres `matchdata_split/`)

A partir da raiz do repositório, com o ambiente Python local a ter `pandas` e `pyarrow` instalados:

```bash
python src/data_extract.py
```

A saída é **`data/csgo_full_dataset.parquet`**. A pasta `matchdata_split/` continua a ser o layout esperado (não entra no Git).

---

## Equipe / GitHub

- **Não** fazer *commit* de arquivos grandes em `data/`.
- Cada pessoa: `git clone` → coloca o Parquet (ou o passo de extract) em `data/` localmente.
- Cópia de `.env`: `cp .env.example .env` e, se quiser, outra porta no `JUPYTER_PORT`.
