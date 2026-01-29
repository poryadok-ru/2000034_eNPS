import psycopg2
from psycopg2.extras import RealDictCursor

class Database:
    def __init__(self, config):
        try:
            self.conn = psycopg2.connect(**config)
        except Exception as e:
            raise e

    def fetch_submissions(self, start, end):
        """Получает данные из БД, фильтруя записи с NULL в rating"""
        try:
            query = """
            SELECT form_name, answers, filiation, department, rating 
            FROM form_submissions 
            WHERE update_at >= %s AND update_at <= %s AND rating IS NOT NULL
            ORDER BY update_at
            """
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (start, end))
                result = cur.fetchall()
                return result
        except Exception as e:
            raise e

    def close(self):
        try:
            self.conn.close()
        except:
            pass