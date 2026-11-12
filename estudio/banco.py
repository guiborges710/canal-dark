"""SQLite do estúdio: decisões, feedback, versões e trabalhos. Sobrevive a fechar a interface e reiniciar o servidor."""
import json
import sqlite3
import threading
from datetime import datetime

from .config import DADOS

ESQUEMA = """
CREATE TABLE IF NOT EXISTS producoes (
  slug TEXT PRIMARY KEY, tema TEXT, formato TEXT DEFAULT 'vertical', estilo TEXT, simulado INTEGER DEFAULT 0,
  origem TEXT NOT NULL, arquivada INTEGER DEFAULT 0, criada_em TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS versoes (
  id INTEGER PRIMARY KEY, slug TEXT NOT NULL, material TEXT NOT NULL, numero INTEGER NOT NULL, hash TEXT NOT NULL,
  manifesto TEXT NOT NULL, deps TEXT NOT NULL, origem TEXT NOT NULL, job_id INTEGER, criada_em TEXT NOT NULL,
  UNIQUE (slug, material, numero));
CREATE TABLE IF NOT EXISTS aprovacoes (  -- vale para uma versão específica
  id INTEGER PRIMARY KEY, slug TEXT NOT NULL, material TEXT NOT NULL, versao_id INTEGER NOT NULL, criada_em TEXT NOT NULL,
  UNIQUE (versao_id));
CREATE TABLE IF NOT EXISTS dispensas_vini (
  id INTEGER PRIMARY KEY, slug TEXT NOT NULL, etapa TEXT NOT NULL, escopo TEXT NOT NULL, hash TEXT NOT NULL, criada_em TEXT NOT NULL,
  UNIQUE (slug, etapa, escopo, hash));
CREATE TABLE IF NOT EXISTS itens (  -- decisão por trecho/asset, presa ao conteúdo: o que não mudou continua aprovado
  id INTEGER PRIMARY KEY, slug TEXT NOT NULL, material TEXT NOT NULL, sha TEXT NOT NULL, decisao TEXT NOT NULL,
  versao_id INTEGER, criada_em TEXT NOT NULL, UNIQUE (slug, material, sha));
CREATE TABLE IF NOT EXISTS feedback (
  id INTEGER PRIMARY KEY, slug TEXT NOT NULL, material TEXT NOT NULL, versao_id INTEGER NOT NULL, item TEXT, cena INTEGER,
  tempo_s REAL, categoria TEXT, texto TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'rascunho', job_id INTEGER,
  criada_em TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY, slug TEXT NOT NULL, etapa TEXT NOT NULL, raia TEXT NOT NULL, titulo TEXT NOT NULL, craque TEXT,
  assinatura TEXT NOT NULL, status TEXT NOT NULL, spec TEXT NOT NULL, pid INTEGER, erro TEXT, resumo TEXT, custo_usd REAL,
  tentativa_de INTEGER, dispensado INTEGER DEFAULT 0, criada_em TEXT NOT NULL, iniciado_em TEXT, terminado_em TEXT);
-- Duplo clique ou recarregar a página não dispara o mesmo trabalho duas vezes: o banco recusa o segundo.
CREATE UNIQUE INDEX IF NOT EXISTS um_job_ativo ON jobs (slug, etapa) WHERE status IN ('fila', 'rodando');
CREATE TABLE IF NOT EXISTS eventos (
  id INTEGER PRIMARY KEY, slug TEXT NOT NULL, texto TEXT NOT NULL, criada_em TEXT NOT NULL);
-- Editor: versões nomeadas do corte, o que cada exportação usou e os clipes de imagem já desenhados.
CREATE TABLE IF NOT EXISTS cortes (
  id INTEGER PRIMARY KEY, slug TEXT NOT NULL, numero INTEGER NOT NULL, assinatura TEXT NOT NULL, sha TEXT NOT NULL, nota TEXT,
  criada_em TEXT NOT NULL, UNIQUE (slug, numero));
CREATE TABLE IF NOT EXISTS exportacoes (
  id INTEGER PRIMARY KEY, slug TEXT NOT NULL, assinatura TEXT NOT NULL, video_sha TEXT NOT NULL, compilado TEXT NOT NULL, criada_em TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS fontes (
  chave TEXT PRIMARY KEY, sha TEXT NOT NULL, dur REAL NOT NULL, origem TEXT NOT NULL, criada_em TEXT NOT NULL);
-- Agentes: o .md em .claude/agents continua sendo a definição; aqui fica só o histórico dele.
CREATE TABLE IF NOT EXISTS agente_versoes (
  id INTEGER PRIMARY KEY, agente TEXT NOT NULL, numero INTEGER NOT NULL, sha TEXT NOT NULL, texto TEXT NOT NULL, origem TEXT NOT NULL,
  criada_em TEXT NOT NULL, UNIQUE (agente, numero));
CREATE TABLE IF NOT EXISTS agente_testes (
  id INTEGER PRIMARY KEY, agente TEXT NOT NULL, versao INTEGER NOT NULL, entrada TEXT NOT NULL, job_id INTEGER, status TEXT NOT NULL,
  saida TEXT, arquivos TEXT, erro TEXT, custo_usd REAL, criada_em TEXT NOT NULL);
-- Fluxos: rascunho editável, versões publicadas imutáveis e execuções presas à versão com que começaram.
CREATE TABLE IF NOT EXISTS fluxos (
  id TEXT PRIMARY KEY, nome TEXT NOT NULL, rascunho TEXT NOT NULL, atualizado_em TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS fluxo_versoes (
  id INTEGER PRIMARY KEY, fluxo TEXT NOT NULL, numero INTEGER NOT NULL, grafo TEXT NOT NULL, nota TEXT, publicada_em TEXT NOT NULL,
  UNIQUE (fluxo, numero));
CREATE TABLE IF NOT EXISTS execucoes (
  id INTEGER PRIMARY KEY, slug TEXT NOT NULL, fluxo TEXT NOT NULL, fluxo_versao INTEGER NOT NULL, fluxo_numero INTEGER NOT NULL, grafo TEXT NOT NULL,
  agentes TEXT NOT NULL, status TEXT NOT NULL, criada_em TEXT NOT NULL, terminada_em TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS uma_execucao_ativa ON execucoes (slug) WHERE status = 'ativa';
CREATE TABLE IF NOT EXISTS exec_nos (
  id INTEGER PRIMARY KEY, exec_id INTEGER NOT NULL, no TEXT NOT NULL, status TEXT NOT NULL, porta TEXT, job_id INTEGER, versao_id INTEGER,
  entrada_hash TEXT, saidas TEXT, nota TEXT, liberado INTEGER DEFAULT 0, forcar INTEGER DEFAULT 0, atualizado_em TEXT NOT NULL, UNIQUE (exec_id, no));
"""
# Colunas novas em bancos que já existiam. Produção antiga fica com NULL e continua no fluxo fixo.
COLUNAS_NOVAS = {"producoes": ("briefing TEXT", "legenda TEXT", "duracao_alvo INTEGER", "idioma TEXT", "estilo_corte TEXT"), "feedback": ("no TEXT",), "jobs": ("motor TEXT", "motor_nota TEXT")}

_local = threading.local()


def agora():
    return datetime.now().isoformat(timespec="seconds")


def con():
    c = getattr(_local, "c", None)
    if c is None:
        DADOS.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(DADOS / "estudio.db", timeout=15, isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA foreign_keys=ON")
        c.executescript(ESQUEMA)
        for tabela, colunas in COLUNAS_NOVAS.items():
            existentes = {r["name"] for r in c.execute(f"PRAGMA table_info({tabela})")}
            for coluna in colunas:
                if coluna.split()[0] not in existentes:
                    try:
                        c.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna}")
                    except sqlite3.OperationalError:
                        pass  # outra conexão acabou de criar
        _local.c = c
    return c


def um(sql, *args):
    r = con().execute(sql, args).fetchone()
    return dict(r) if r else None


def varios(sql, *args):
    return [dict(r) for r in con().execute(sql, args).fetchall()]


def faz(sql, *args):
    return con().execute(sql, args)


def evento(slug, texto):
    faz("INSERT INTO eventos (slug, texto, criada_em) VALUES (?, ?, ?)", slug, texto, agora())


def versao_dict(v):
    if v:
        v["manifesto"] = json.loads(v["manifesto"])
        v["deps"] = json.loads(v["deps"])
    return v
