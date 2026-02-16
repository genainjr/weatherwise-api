"""
Script de inicialização do banco de dados
Popula collection de cidades e configura índices
"""
import os
from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Pegar connection string
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "weatherwise")

if not MONGODB_URI:
    print("❌ Erro: MONGODB_URI não encontrada no .env")
    print("Certifique-se que o arquivo .env existe e contém MONGODB_URI")
    exit(1)

# Lista de cidades para monitorar
CITIES_DATA = [
    {
        "name": "Fortaleza",
        "country": "BR",
        "lat": -3.7172,
        "lon": -38.5433,
        "timezone": "America/Fortaleza",
        "active": True
    },
    {
        "name": "São Paulo",
        "country": "BR",
        "lat": -23.5505,
        "lon": -46.6333,
        "timezone": "America/Sao_Paulo",
        "active": True
    },
    {
        "name": "Rio de Janeiro",
        "country": "BR",
        "lat": -22.9068,
        "lon": -43.1729,
        "timezone": "America/Sao_Paulo",
        "active": True
    },
    {
        "name": "Salvador",
        "country": "BR",
        "lat": -12.9714,
        "lon": -38.5014,
        "timezone": "America/Bahia",
        "active": True
    },
    {
        "name": "Recife",
        "country": "BR",
        "lat": -8.0476,
        "lon": -34.877,
        "timezone": "America/Recife",
        "active": True
    }
]


def init_database():
    """Inicializa banco de dados"""
    print("🚀 Inicializando banco de dados WeatherWise...")
    print(f"📍 Database: {MONGODB_DB_NAME}")
    
    try:
        # Conectar ao MongoDB
        print("\n🔌 Conectando ao MongoDB Atlas...")
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        
        # Testar conexão
        client.admin.command('ping')
        print("✅ Conectado ao MongoDB com sucesso!")
        
        # Selecionar database
        db = client[MONGODB_DB_NAME]
        
        # Criar índices
        print("\n📑 Criando índices...")
        
        # Cities
        db.cities.create_index([("name", ASCENDING), ("country", ASCENDING)], unique=True)
        
        # Weather Current - TTL index para auto-delete após 180 dias
        db.weather_current.create_index([("timestamp", DESCENDING)], expireAfterSeconds=15552000)
        db.weather_current.create_index([("city_id", ASCENDING)])
        
        # Weather Forecast
        db.weather_forecast.create_index([("city_id", ASCENDING)])
        db.weather_forecast.create_index([("target_timestamp", DESCENDING)])
        
        # Historical
        db.weather_historical.create_index([("city_id", ASCENDING), ("date", DESCENDING)])
        
        print("✅ Índices criados!")
        
        # Inserir cidades
        print("\n🏙️  Inserindo cidades...")
        inserted_count = 0
        updated_count = 0
        
        for city_data in CITIES_DATA:
            # Verificar se cidade já existe
            existing = db.cities.find_one({
                "name": city_data["name"],
                "country": city_data["country"]
            })
            
            if existing:
                # Atualizar dados
                db.cities.update_one(
                    {"_id": existing["_id"]},
                    {"$set": city_data}
                )
                updated_count += 1
                print(f"  ✏️  Atualizada: {city_data['name']}, {city_data['country']}")
            else:
                # Inserir nova cidade
                city_data["created_at"] = datetime.utcnow()
                db.cities.insert_one(city_data)
                inserted_count += 1
                print(f"  ✅ Inserida: {city_data['name']}, {city_data['country']}")
        
        print(f"\n📊 Resumo:")
        print(f"   Cidades inseridas: {inserted_count}")
        print(f"   Cidades atualizadas: {updated_count}")
        print(f"   Total de cidades: {len(CITIES_DATA)}")
        
        # Verificar collections
        collections = db.list_collection_names()
        print(f"\n📁 Collections criadas: {', '.join(collections) if collections else 'Nenhuma ainda'}")
        
        # Contar documentos
        cities_count = db.cities.count_documents({})
        print(f"📍 Total de cidades no banco: {cities_count}")
        
        # Fechar conexão
        client.close()
        
        print("\n✅ Inicialização concluída com sucesso!")
        print("\n🚀 Próximo passo:")
        print("   uvicorn app.main:app --reload")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante inicialização: {str(e)}")
        print("\n🔍 Verificações:")
        print("   1. MONGODB_URI está correto no .env?")
        print("   2. Seu IP está na whitelist do MongoDB Atlas?")
        print("   3. A senha não contém caracteres especiais não-encoded?")
        print("   4. Internet está funcionando?")
        return False


if __name__ == "__main__":
    import sys
    success = init_database()
    sys.exit(0 if success else 1)