import logging
from ..db import get_connection

# ---------------------------
# Додає скаргу в БД
# ---------------------------
def send_complaint(applicant_id: int, violator_id: int, reason_id: int, extra_description: str = None) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if extra_description:
            cursor.execute("""
                        INSERT INTO complaints (applicant_id, violator_id, reason_id, extra_description)
                        VALUES (%s, %s, %s, %s)
                    """, (applicant_id, violator_id, reason_id, extra_description))
        else:
            cursor.execute("""
                        INSERT INTO complaints (applicant_id, violator_id, reason_id)
                        VALUES (%s, %s, %s)
                    """, (applicant_id, violator_id, reason_id))
        conn.commit()
        return True
    except Exception as e:
        logging.exception(e)
        return False
    finally:
        cursor.close()
        conn.close()