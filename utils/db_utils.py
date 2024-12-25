import random
import mysql.connector
from utils.db_config import DB_CONFIG


# 데이터베이스에서 랜덤으로 카테고리를 가져오기
def fetch_available_categories():
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("SELECT place_category_id FROM place_category")  # place_category 테이블에서 ID 가져오기
        categories = [row[0] for row in cursor.fetchall()]  # 결과를 리스트로 변환
        return categories
    except mysql.connector.Error as err:
        print(f"DB 에러 발생: {err}")
        return []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# 데이터베이스에서 랜덤으로 회원의 memberId를 가져오기
def fetch_random_member_id():
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id FROM member WHERE id IS NOT NULL ORDER BY RAND() LIMIT 1")  # member 테이블에서 랜덤으로 1명 선택
        result = cursor.fetchone()
        if result:
            print(f"랜덤으로 선택된 memberId: {result['id']}")
            return result['id']  # memberId 반환
        else:
            raise ValueError("데이터베이스에 저장된 회원이 없습니다.")
    except mysql.connector.Error as err:
        print(f"DB 에러 발생: {err}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def fetch_random_group_id(member_id):
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        # 본인이 생성하거나 가입하지 않은 랜덤 모임 가져오기
        query = """
            SELECT group_id
            FROM groups
            WHERE group_id NOT IN (
                SELECT group_id FROM group_member WHERE member_id = %s
            )
            AND group_id NOT IN (
                SELECT group_id 
                FROM group_member
                WHERE member_id = %s AND role = 'ADMIN'
            )
            AND recruiting = TRUE
            ORDER BY RAND() LIMIT 1
            """
        cursor.execute(query, (member_id, member_id))
        result = cursor.fetchone()

        if result:
            return result['group_id']
        else:
            print("사용 가능한 랜덤 모임이 없습니다.")
            return None
    except mysql.connector.Error as err:
        print(f"DB 에러 발생: {err}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# DB에서 모든 신청 데이터를 조회
def fetch_all_applications():
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        # 모든 신청 조회 쿼리
        query = "SELECT application_id, group_id FROM application"
        cursor.execute(query)

        applications = cursor.fetchall()  # 모든 신청 데이터 가져오기
        return applications
    except mysql.connector.Error as err:
        print(f"DB 에러 발생: {err}")
        return []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# 특정 그룹에서 사용자가 ADMIN인지 확인
def check_role(member_id, group_id):
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        # ADMIN 확인 쿼리
        query = """
        SELECT role 
        FROM group_member 
        WHERE group_id = %s AND member_id = %s
        """
        cursor.execute(query, (group_id, member_id))
        result = cursor.fetchone()

        # role이 ADMIN인지 확인
        if result and result.get('role') == 'ADMIN':
            return True
        return False

    except mysql.connector.Error as err:
        print(f"DB 에러 발생: {err}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# 특정 그룹의 ADMIN 사용자 조회
def get_admin(group_id):
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT m.email, m.password 
            FROM member m
            JOIN group_member gm ON m.id = gm.member_id
            WHERE gm.group_id = %s AND gm.role = 'ADMIN'
            LIMIT 1
            """
        cursor.execute(query, (group_id,))
        result = cursor.fetchone()

        if result:
            print(f"그룹 {group_id}의 ADMIN 사용자: {result['email']}")
            return result
        else:
            print(f"그룹 {group_id}의 ADMIN 사용자를 찾을 수 없습니다.")
            return None
    except mysql.connector.Error as err:
        print(f"DB 에러 발생: {err}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# 선호 카테고리를 설정하고 선호카테고리 상태를 DONE으로 변경
def set_prefer_category(member_id):
    connection = None
    try:
        # DB 연결
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # 사용 가능한 카테고리 가져오기
        available_categories = fetch_available_categories()
        if not available_categories:
            print("사용 가능한 카테고리가 없습니다.")
            return

        # 랜덤으로 3개의 선호 카테고리 선택
        categories = random.sample(available_categories, 3)

        # member_preference_category 테이블에 카테고리 추가
        for category_id in categories:
            query = """
            INSERT INTO member_preference_category (member_id, place_category_place_category_id)
            VALUES (%s, %s)
            """
            cursor.execute(query, (member_id, category_id))
        connection.commit()
        print(f"memberId={member_id}에 대한 선호 카테고리 추가 완료: {categories}")

        # member 테이블에서 is_prefer_category를 'DONE'으로 업데이트
        update_query = """
        UPDATE member
        SET is_prefer_category = 'DONE'
        WHERE id = %s
        """
        cursor.execute(update_query, (member_id,))
        connection.commit()
        print(f"memberId={member_id}의 선호 카테고리를 'DONE'으로 업데이트 완료")

    except mysql.connector.Error as err:
        print(f"DB 에러 발생: {err}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
