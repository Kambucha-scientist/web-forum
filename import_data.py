import os
import sys
import re
from sqlalchemy import create_engine, text

def import_sql_file(filepath):
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)
    
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    engine = create_engine(database_url)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Удаляем всё, что не является SQL: строки с Owner, Type, Schema, SET, SELECT pg_catalog
    # Оставляем только INSERT, CREATE TABLE (если есть), и чистые данные
    lines = content.split('\n')
    filtered_lines = []
    for line in lines:
        stripped = line.strip()
        # Пропускаем служебные строки pg_dump
        if any(stripped.startswith(prefix) for prefix in [
            '--', 'SET ', 'SELECT pg_catalog', 'Owner:', 'Type:', 'Schema:',
            'GRANT ', 'REVOKE ', 'CREATE EXTENSION', 'COMMENT ON'
        ]):
            continue
        # Пропускаем пустые строки в начале/конце
        if not stripped:
            continue
        filtered_lines.append(line)
    
    sql = '\n'.join(filtered_lines)
    
    # Разбиваем на отдельные команды (только INSERT)
    # Ищем все INSERT-выражения
    pattern = r'INSERT INTO[^;]+;'
    commands = re.findall(pattern, sql, re.IGNORECASE)
    
    if not commands:
        print("No INSERT commands found!")
        return
    
    print(f"Found {len(commands)} INSERT commands")
    
    # Выполняем каждый INSERT отдельно
    with engine.connect() as conn:
        for i, cmd in enumerate(commands):
            try:
                conn.execute(text(cmd))
                conn.commit()
                print(f"OK: {i+1}/{len(commands)}")
            except Exception as e:
                print(f"SKIP {i+1}: {str(e)[:100]}")
                # Откатываем неудачную транзакцию и продолжаем
                conn.rollback()
    
    print("Import completed!")

if __name__ == '__main__':
    import_sql_file('data.sql')