from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Table
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Projeto(Base):
    __tablename__ = 'projeto'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    data_criacao = Column(DateTime, default=datetime.now)
    observacoes_metodologicas = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Projeto(nome='{self.nome}')>"

class Sujeito(Base):
    __tablename__ = 'sujeito'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_pseudonimo = Column(String(255), nullable=False, unique=True)
    nome_opcional = Column(String(255), nullable=True)
    idade = Column(Integer, nullable=True)
    genero = Column(String(100), nullable=True)
    sexualidade = Column(String(100), nullable=True)
    raca_cor = Column(String(100), nullable=True)
    escolaridade = Column(String(255), nullable=True)
    renda = Column(String(100), nullable=True)
    filhos = Column(Integer, nullable=True)
    municipio = Column(String(255), nullable=True)
    bairro = Column(String(255), nullable=True)
    vila = Column(String(255), nullable=True)
    rua = Column(String(255), nullable=True)
    numero = Column(String(50), nullable=True)
    
    # Novos campos solicitados do autor
    autor = Column(String(255), nullable=True)
    idade_autor = Column(Integer, nullable=True)
    bairro_autor = Column(String(255), nullable=True)
    reincidencia_autor = Column(String(100), nullable=True)
    reincidencia_vitima = Column(String(100), nullable=True)
    registro = Column(String(100), nullable=True)
    ano = Column(Integer, nullable=True)
    sexo_autor = Column(String(100), nullable=True)
    escolaridade_autor = Column(String(255), nullable=True)

    # Relacionamentos
    entrevistas = relationship("Entrevista", back_populates="sujeito")
    evocacoes = relationship("Evocacao", back_populates="sujeito", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sujeito(codigo='{self.codigo_pseudonimo}')>"

class Entrevista(Base):
    __tablename__ = 'entrevista'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    nome_arquivo_original = Column(String(255), nullable=False)
    caminho_relativo_arquivo = Column(String(512), nullable=False)
    texto_extraido = Column(Text, nullable=False)
    data_importacao = Column(DateTime, default=datetime.now)
    
    sujeito_id = Column(Integer, ForeignKey('sujeito.id', ondelete='SET NULL'), nullable=True)
    
    # Relacionamentos
    sujeito = relationship("Sujeito", back_populates="entrevistas")
    evocacoes = relationship("Evocacao", back_populates="entrevista", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Entrevista(titulo='{self.titulo}')>"

class CategoriaDiscursiva(Base):
    __tablename__ = 'categoria_discursiva'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False, unique=True)
    descricao = Column(Text, nullable=True)
    observacoes = Column(Text, nullable=True)
    
    # Relacionamentos
    evocacoes = relationship("Evocacao", back_populates="categoria")

    def __repr__(self):
        return f"<CategoriaDiscursiva(nome='{self.nome}')>"

class EspacialidadeDiscursiva(Base):
    __tablename__ = 'espacialidade_discursiva'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False, unique=True)
    descricao = Column(Text, nullable=True)
    observacoes = Column(Text, nullable=True)
    
    # Relacionamentos
    evocacoes = relationship("Evocacao", back_populates="espacialidade")

    def __repr__(self):
        return f"<EspacialidadeDiscursiva(nome='{self.nome}')>"

class Evocacao(Base):
    __tablename__ = 'evocacao'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    entrevista_id = Column(Integer, ForeignKey('entrevista.id', ondelete='CASCADE'), nullable=False)
    sujeito_id = Column(Integer, ForeignKey('sujeito.id', ondelete='SET NULL'), nullable=True)
    categoria_id = Column(Integer, ForeignKey('categoria_discursiva.id'), nullable=False)
    espacialidade_id = Column(Integer, ForeignKey('espacialidade_discursiva.id'), nullable=False)
    
    trecho_literal = Column(Text, nullable=False)
    posicao_inicial = Column(Integer, nullable=False)
    posicao_final = Column(Integer, nullable=False)
    
    elementos = Column(Text, nullable=True)
    sujeito_relacao = Column(String(255), nullable=True)
    observacoes_analiticas = Column(Text, nullable=True)
    
    data_criacao = Column(DateTime, default=datetime.now)
    data_edicao = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    entrevista = relationship("Entrevista", back_populates="evocacoes")
    sujeito = relationship("Sujeito", back_populates="evocacoes")
    categoria = relationship("CategoriaDiscursiva", back_populates="evocacoes")
    espacialidade = relationship("EspacialidadeDiscursiva", back_populates="evocacoes")

    def __repr__(self):
        return f"<Evocacao(id={self.id}, trecho_curto='{self.trecho_literal[:20]}...')>"
