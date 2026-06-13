import os
import sys
from sqlalchemy import create_engine, text

def import_sql_file(filepath):
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)
    
    # Замена postgres:// на postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    engine = create_engine(database_url)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Разбиваем на отдельные команды по точке с запятой
    commands = sql.split(';')
    
    with engine.connect() as conn:
        for cmd in commands:
            cmd = cmd.strip()
            if cmd and not cmd.startswith('--'):
                try:
                    conn.execute(text(cmd))
                    conn.commit()
                except Exception as e:
                    print(f"Skipping command due to: {e}")
    
    print("Import completed!")

if __name__ == '__main__':
    import_sql_file('data.sql')