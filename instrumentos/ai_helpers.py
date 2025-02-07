from openai import OpenAI
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)

client = None

def setup_openai(api_key=None):
    """Configura a API key da OpenAI"""
    global client
    key_to_use = api_key or os.getenv('OPENAI_API_KEY') or settings.OPENAI_API_KEY
    logger.info(f"Using API key: {key_to_use[:6]}...{key_to_use[-4:] if key_to_use else 'None'}")
    
    if not key_to_use:
        raise ValueError("OpenAI API key not found in settings or environment")
        
    client = OpenAI(api_key=key_to_use)

def generate_categorias(quantidade):
    """Gera categorias de instrumentos musicais usando GPT"""
    prompt = f"""
    Gere {quantidade} categorias de instrumentos musicais no formato JSON.
    Cada categoria deve ter:
    - nome: nome único da categoria
    - descricao: breve descrição da categoria
    
    Exemplo:
    [
        {{"nome": "Cordas", "descricao": "Instrumentos que produzem som através da vibração de cordas"}},
        {{"nome": "Sopro", "descricao": "Instrumentos que produzem som através da vibração do ar"}}
    ]
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content

def generate_subcategorias(quantidade, categoria):
    """Gera subcategorias para uma categoria específica"""
    prompt = f"""
    Gere {quantidade} subcategorias de instrumentos musicais para a categoria "{categoria.nome}" no formato JSON.
    Cada subcategoria deve ter:
    - nome: nome único da subcategoria
    - descricao: breve descrição da subcategoria
    
    Exemplo para categoria "Cordas":
    [
        {{"nome": "Violões", "descricao": "Instrumentos de cordas dedilhadas com caixa acústica"}},
        {{"nome": "Violinos", "descricao": "Instrumentos de cordas friccionadas com arco"}}
    ]
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content

def generate_marcas(quantidade):
    """Gera marcas de instrumentos musicais"""
    prompt = f"""
    Gere {quantidade} marcas de instrumentos musicais no formato JSON.
    Cada marca deve ter:
    - nome: nome único da marca
    - pais_origem: país de origem da marca
    - website: site oficial da marca (use domínios reais)
    
    Exemplo:
    [
        {{"nome": "Yamaha", "pais_origem": "Japão", "website": "https://yamaha.com"}},
        {{"nome": "Fender", "pais_origem": "Estados Unidos", "website": "https://fender.com"}}
    ]
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content

def generate_modelos(quantidade, marca):
    """Gera modelos para uma marca específica"""
    prompt = f"""
    Gere {quantidade} modelos de instrumentos musicais para a marca "{marca.nome}" no formato JSON.
    Cada modelo deve ter:
    - nome: nome único do modelo
    - descricao: breve descrição do modelo
    - subcategoria: nome de uma subcategoria existente (exemplo: "Violões", "Guitarras", "Baixos", etc)
    
    Exemplo para marca "Yamaha":
    [
        {{"nome": "F310", "descricao": "Violão acústico iniciante com cordas de aço", "subcategoria": "Violões"}},
        {{"nome": "PSR-E373", "descricao": "Teclado arranjador com 61 teclas sensíveis ao toque", "subcategoria": "Teclados"}}
    ]
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content
