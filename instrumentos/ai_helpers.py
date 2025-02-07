from openai import OpenAI
from django.conf import settings
import logging
import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from PIL import Image
from io import BytesIO

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
    - nome: nome da marca
    - pais_origem: país de origem da marca
    - website: website oficial da marca (URL real e válida)
    - logotipo_url: URL real e válida do logotipo da marca (preferencialmente PNG transparente)
    
    Exemplo:
    [
        {{
            "nome": "Fender",
            "pais_origem": "Estados Unidos",
            "website": "https://www.fender.com",
            "logotipo_url": "https://upload.wikimedia.org/wikipedia/commons/9/92/Fender_guitars_logo.png"
        }}
    ]

    Observações:
    1. Use apenas marcas reais e famosas de instrumentos musicais
    2. Use apenas URLs reais e válidas para websites e logotipos
    3. Prefira logotipos em PNG com fundo transparente
    4. Prefira logotipos de alta resolução
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

def generate_instrumentos(quantidade, modelo):
    """Gera instrumentos para um modelo específico"""
    prompt = f"""
    Gere {quantidade} instrumentos musicais para o modelo "{modelo.nome}" da marca "{modelo.marca.nome}" no formato JSON.
    Cada instrumento deve ter:
    - codigo: código único do instrumento (formato: [marca_sigla][modelo_sigla][número], ex: FEN_ST_001)
    - numero_serie: número de série aleatório (alfanumérico)
    - ano_fabricacao: ano entre 1990 e 2024
    - preco: preço de compra entre 500 e 50000
    - valor_mercado: valor de mercado atual (pode ser maior ou menor que o preço de compra)
    - estado_conservacao: um dos valores: ["novo", "excelente", "muito_bom", "bom", "regular", "ruim"]
    - status: um dos valores: ["disponivel", "vendido", "reservado", "manutencao"]
    - caracteristicas: características específicas do instrumento
    - descricao: descrição detalhada do instrumento
    
    Exemplo para modelo "Stratocaster" da marca "Fender":
    [
        {{
            "codigo": "FEN_ST_001",
            "numero_serie": "US21345678",
            "ano_fabricacao": 2021,
            "preco": 8500.00,
            "valor_mercado": 9200.00,
            "estado_conservacao": "excelente",
            "status": "disponivel",
            "caracteristicas": "Corpo em alder, braço em maple, escala em rosewood, 22 trastes, 3 captadores single-coil",
            "descricao": "Guitarra Fender Stratocaster American Professional II em Sunburst. Excelente estado, todas as peças originais, acompanha case original e certificado de autenticidade."
        }}
    ]
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content

def buscar_logo_no_site(site_url):
    """
    Busca logo no site usando várias estratégias
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Timeout de 5 segundos para não travar
        response = requests.get(site_url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Lista para armazenar possíveis URLs de logo
        logo_candidates = []
        
        # 1. Verifica meta tags (Open Graph/Twitter)
        for meta in soup.find_all('meta', property=['og:image', 'twitter:image']):
            if meta.get('content'):
                logo_candidates.append(urljoin(site_url, meta['content']))
        
        # 2. Busca imagens com 'logo' no nome/alt/class
        for img in soup.find_all('img', src=True):
            src = img['src']
            alt = img.get('alt', '').lower()
            class_name = ' '.join(img.get('class', [])).lower()
            
            # Padrões comuns de nomes de logos
            if any(pattern in src.lower() or pattern in alt or pattern in class_name 
                  for pattern in ['logo', 'brand', 'header-image', 'site-logo']):
                logo_candidates.append(urljoin(site_url, src))
        
        # 3. Busca SVGs (comum para logos)
        for svg in soup.find_all(['svg', 'object'], class_=True):
            if any(pattern in ' '.join(svg.get('class', [])).lower() 
                  for pattern in ['logo', 'brand']):
                if svg.get('data'):
                    logo_candidates.append(urljoin(site_url, svg['data']))
        
        # 4. Verifica cada candidato
        for url in logo_candidates:
            try:
                # Verifica se a URL é válida
                img_response = requests.head(url, headers=headers, timeout=3)
                if img_response.status_code == 200:
                    # Verifica o content-type
                    content_type = img_response.headers.get('content-type', '')
                    if any(t in content_type.lower() for t in ['image', 'svg']):
                        # Se for imagem, verifica o tamanho
                        if 'image' in content_type:
                            img_data = requests.get(url, headers=headers, timeout=3)
                            img = Image.open(BytesIO(img_data.content))
                            width, height = img.size
                            # Logo deve ter tamanho razoável
                            if width >= 100 and height >= 100:
                                return url
                        else:  # Se for SVG, aceita
                            return url
            except:
                continue
        
        # 5. Fallback: favicon em alta resolução
        favicon_patterns = [
            '/favicon-32x32.png',
            '/favicon-96x96.png',
            '/apple-touch-icon.png',
            '/apple-touch-icon-precomposed.png',
            '/favicon.ico'
        ]
        
        for pattern in favicon_patterns:
            try:
                favicon_url = urljoin(site_url, pattern)
                response = requests.head(favicon_url, headers=headers, timeout=2)
                if response.status_code == 200:
                    return favicon_url
            except:
                continue
                
    except Exception as e:
        logger.error(f"Erro ao buscar logo no site {site_url}: {str(e)}")
    
    return None

def generate_logo_url(marca_nome):
    """Gera URL do logotipo para uma marca específica"""
    # Mapeamento de marcas para seus domínios
    dominios_conhecidos = {
        'fender': 'fender.com',
        'gibson': 'gibson.com',
        'ibanez': 'ibanez.com',
        'yamaha': 'yamaha.com',
        'roland': 'roland.com',
        'marshall': 'marshall.com',
        'gretsch': 'gretsch.com',
        'epiphone': 'epiphone.com',
        'esp': 'espguitars.com',
        'prs': 'prsguitars.com',
        'jackson': 'jacksonguitars.com',
        'schecter': 'schecterguitars.com',
        'dean': 'deanguitars.com',
        'washburn': 'washburn.com',
        'bc rich': 'bcrich.com',
        'cort': 'cortguitars.com',
        'kramer': 'kramerguitars.com',
        'guild': 'guildguitars.com',
        'rickenbacker': 'rickenbacker.com',
        'charvel': 'charvel.com',
        'evh': 'evhgear.com',
        'ernie ball': 'ernieball.com',
        'music man': 'music-man.com',
        'squier': 'fender.com/squier',
        'martin': 'martinguitar.com',
        'taylor': 'taylorguitars.com',
        'zildjian': 'zildjian.com',
        'sabian': 'sabian.com',
        'pearl': 'pearldrum.com'
    }
    
    try:
        # Tentar encontrar uma correspondência exata
        dominio = dominios_conhecidos.get(marca_nome.lower())
        
        # Se não encontrar, tentar encontrar uma correspondência parcial
        if not dominio:
            for known_brand, known_domain in dominios_conhecidos.items():
                if known_brand in marca_nome.lower() or marca_nome.lower() in known_brand:
                    dominio = known_domain
                    break
        
        if dominio:
            # 1. Tentar Clearbit primeiro
            clearbit_url = f"https://logo.clearbit.com/{dominio}"
            try:
                response = requests.head(clearbit_url)
                if response.status_code == 200:
                    return json.dumps({"logotipo_url": clearbit_url})
            except:
                pass
            
            # 2. Se Clearbit falhar, tentar scraping
            site_url = f"https://{dominio}"
            logo_url = buscar_logo_no_site(site_url)
            if logo_url:
                return json.dumps({"logotipo_url": logo_url})
        
        # 3. Se nada funcionar, gerar descrição
        prompt = f"""
        Descreva como deve ser o logotipo da marca de instrumentos musicais "{marca_nome}".
        Considere:
        1. As cores tradicionais da marca
        2. O estilo do texto
        3. Elementos visuais característicos
        4. História e identidade da marca
        
        Retorne a descrição em até 100 palavras.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        description = response.choices[0].message.content.strip()
        logger.info(f"Descrição gerada para {marca_nome}: {description}")
        
        # Retornar um erro amigável
        return json.dumps({
            "error": f"Logotipo não encontrado para {marca_nome}",
            "description": description
        })
            
    except Exception as e:
        logger.error(f"Erro ao gerar URL do logotipo para {marca_nome}: {str(e)}")
        return json.dumps({"error": str(e)})
