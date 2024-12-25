import random
import mysql.connector
import requests
from utils.db_utils import fetch_random_group_id, set_prefer_category
from utils.generate_ import generate
from faker import Faker


class AutoWorkByLoginRegister:
    def __init__(self, **kwargs):
        self.server_host = kwargs.get('server_host', 'localhost')
        self.server_port = kwargs.get('server_port', '8000')
        self.db_host = kwargs.get('db_host', 'localhost')
        self.db_port = kwargs.get('db_port', 3306)
        self.db_user = kwargs.get('db_user', 'root')
        self.db_password = kwargs.get('db_password', '')
        self.db_database = kwargs.get('db_database', 'test')
        self.api = f'http://{self.server_host}:{self.server_port}/api/v1'
        self.session = requests.Session()
        self.fake = Faker('ko_KR')
        self.member_id = None

    def _get_db_connection(self):
        return mysql.connector.connect(
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

    # 로그인
    def login(self, email=None, password=None):
        connection = None
        try:
            if not email or not password:
                connection = self._get_db_connection()
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT id, email, password FROM member ORDER BY RAND() LIMIT 1")
                user = cursor.fetchone()

                if not user:
                    print("사용자를 찾을 수 없습니다.")
                    return False

                email, password = user['email'], user['password']

            response = self.session.put(f"{self.api}/member/login", json={'email': email, 'password': password})

            if response.status_code == 200:
                self.member_id = response.json()['id']
                print(f"로그인 성공: {email}, memberId: {self.member_id}")
                return response.json()
            else:
                print(f"로그인 실패: {email}")
                return False

        except mysql.connector.Error as err:
            print(f"DB 에러 발생: {err}")
            return False
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    # 회원가입
    def register(self):
        data = generate()
        print(f"생성된 사용자 데이터: {data}")

        response = self.session.post(f"{self.api}/member/register", json=data,
                                     headers={'Content-Type': 'application/json'})
        print(f"회원가입 응답 코드: {response.status_code}")
        print(f"회원가입 응답 내용: {response.text}")

        if response.status_code == 201:
            login_success = self.login(data['email'], data['password'])
            if login_success:
                self.member_id = login_success.get('id')
                print(f"로그인 성공! memberId: {self.member_id}")

                print(f"memberId={self.member_id}에 대해 선호 카테고리 설정 시작")
                set_prefer_category(self.member_id)
                print(f"memberId={self.member_id}에 대한 선호 카테고리 설정 완료")
                return data
        else:
            print(f"회원가입 실패: {response.status_code}, {response.text}")
            return None

    def run(self):
        choice_num = random.choice([1, 2, 3, 4])

        if choice_num in [1, 2]:
            print("로그인을 실행합니다.")
            login_response = self.login()
            if login_response:
                print(f"로그인 성공! 사용자 정보: {login_response}")
            else:
                print("로그인 실패")

        elif choice_num in [3, 4]:
            print("회원가입을 실행합니다.")
            user_data = self.register()
            if user_data:
                print(f"회원가입 및 선호 카테고리 설정 완료: {user_data}")
            else:
                print("회원가입 실패")

        else:
            print("잘못된 선택입니다. 프로그램을 종료합니다.")
