from django.core.management.base import BaseCommand
from instrumentos.models import Categoria, Modelo, Marca, SubCategoria, Classe
import openai
import json
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

class Command(BaseCommand):
    help = 'Popula o banco de dados com categorias, modelos e marcas usando IA'

    def handle(self, *args, **kwargs):
        try:
            api_key = os.getenv('OPENAI_API_KEY')

            if not api_key:
                raise ValueError("API key não encontrada. Verifique se o .env está correto.")

            # Criar cliente OpenAI corretamente
            client = openai.OpenAI(api_key=api_key)

            # Fazer a chamada para a API
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um especialista em instrumentos musicais."},
                    {"role": "user", "content": self.get_prompt()}
                ]
            )

            # Converter resposta para JSON
            data = json.loads(response.choices[0].message.content)

            # Criar categorias e subcategorias
            for cat_data in data['categorias']:
                categoria, _ = Categoria.objects.get_or_create(
                    nome=cat_data['nome'],
                    descricao=cat_data['descricao']
                )
                self.stdout.write(f"Categoria criada: {cat_data['nome']}")
                
                # Criar subcategorias para esta categoria
                for subcat in cat_data['subcategorias']:
                    SubCategoria.objects.get_or_create(
                        nome=subcat['nome'],
                        descricao=subcat['descricao'],
                        categoria=categoria
                    )
                    self.stdout.write(f"Subcategoria criada: {subcat['nome']}")

            # Criar marcas
            for marca in data['marcas']:
                Marca.objects.get_or_create(
                    nome=marca['nome'],
                    pais_origem=marca['pais_origem'],
                    website=marca['website']
                )
                self.stdout.write(f"Marca criada: {marca['nome']}")

            # Criar modelos
            for modelo in data['modelos']:
                Modelo.objects.get_or_create(
                    nome=modelo['nome'],
                    descricao=modelo['descricao']
                )
                self.stdout.write(f"Modelo criado: {modelo['nome']}")

            self.stdout.write(self.style.SUCCESS('Dados populados com sucesso!'))

        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR('Erro ao decodificar resposta da API')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro inesperado: {str(e)}')
            )

def get_prompt(self):
        return """
        Gere uma lista em formato JSON com dados de instrumentos musicais contendo:
        1. 10 categorias de instrumentos (nome, descrição e subcategorias)
        2. 20 marcas famosas (nome, país de origem e website)
        3. 30 modelos populares (nome e descrição)
        
        Para cada categoria, inclua 3-5 subcategorias relevantes.
        
        Formato:
        {
            "categorias": [
                {
                    "nome": "",
                    "descricao": "",
                    "subcategorias": [
                        {
                            "nome": "",
                            "descricao": ""
                        }
                    ]
                }
            ],
            "marcas": [{"nome": "", "pais_origem": "", "website": ""}],
            "modelos": [{"nome": "", "descricao": ""}]
        }
        """ 		            

	