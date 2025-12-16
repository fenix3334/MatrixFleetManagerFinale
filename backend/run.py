"""
Entry point Backend API - Matrix Fleet Manager
"""
import os
from app import create_app

# Determina ambiente
env = os.getenv('FLASK_ENV', 'development')

# Crea app
app = create_app(env)

if __name__ == '__main__':
    # Esegui server di sviluppo
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=(env == 'development')
    )
