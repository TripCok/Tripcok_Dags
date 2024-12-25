import mysql.connector
import requests
from utils.db_utils import fetch_random_group_id, fetch_all_applications, get_admin
from utils.generate_ import generate

class AutoWorkByGroupJoin:
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
                print(f"로그인 성공: {email}, memberId: {response.json()['id']}")
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

        response = self.session.post(f"{self.api}/member/register", json=data, headers={'Content-Type': 'application/json'})
        print(f"회원가입 응답 코드: {response.status_code}")
        print(f"회원가입 응답 내용: {response.text}")

        if response.status_code == 201:
            login_success = self.login(data['email'], data['password'])
            return data if login_success else None
        else:
            print(f"회원가입 실패: {response.status_code}, {response.text}")

    # 모임 생성
    def create_group(self, group_data):
        print(f"생성된 모임 데이터: {group_data}")
        headers = {'Content-Type': 'application/json'}
        response = self.session.post(f"{self.api}/group", json=group_data, headers=headers)
        print(f"모임 생성 응답 코드: {response.status_code}")
        print(f"모임 생성 응답 내용: {response.text}")

        if response.status_code == 201:
            return response.json()
        else:
            print(f"모임 생성 실패: {response.status_code}, {response.text}")
            return None

    # 모임 신청
    def create_application(self, member_id):
        headers = {'Content-Type': 'application/json'}
        try:
            group_id = fetch_random_group_id(member_id)
            if not group_id:
                print("모임을 찾을 수 없습니다")
                return None

            application_data = {
                "memberId": member_id,
                "groupId": group_id
            }

            response = self.session.post(f"{self.api}/application", json=application_data, headers=headers)
            print(f"모임 신청 응답 코드: {response.status_code}")
            print(f"모임 신청 응답 내용: {response.text}")

            if response.status_code == 201:
                return response.text
            else:
                print(f"모임 신청 실패: {response.status_code}, {response.text}")
                return None

        except Exception as e:
            print(f"모임 신청 중 예외 발생: {str(e)}")
            return None

    # 모임 수락
    def accept_application(self, group_admin_id, application_id):
        headers = {'Content-Type': 'application/json'}
        try:
            accept_data = {
                "groupAdminId": group_admin_id,
                "applicationId": application_id
            }

            response = self.session.put(f"{self.api}/application", json=accept_data, headers=headers)
            print(f"모임 신청 수락 응답 코드: {response.status_code}")

            if response.status_code == 200:
                return response.text
            else:
                print("모임 신청 수락 실패: 상태 코드가 200이 아닙니다.")
                return None
        except Exception as e:
            print(f"모임 신청 수락 중 예외 발생: {str(e)}")
            return None

    def run(self):
        print("DB에서 신청 목록 조회 및 수락을 실행합니다.")

        # DB에서 모든 신청 조회
        applications = fetch_all_applications()
        if not applications:
            print("DB에서 신청 데이터를 찾을 수 없습니다.")
        else:
            print(f"조회된 신청 목록: {applications}")

            # 신청 처리
            for application in applications:
                application_id = application.get('application_id')
                group_id = application.get('group_id')

                if not group_id:
                    print(f"신청 ID {application_id}: group_id 정보 없음, 건너뜀")
                    continue

                # 그룹의 ADMIN 사용자 가져오기
                admin_user = get_admin(group_id)
                if not admin_user:
                    print(f"그룹 {group_id}의 ADMIN 사용자를 찾을 수 없어 신청을 건너뜁니다.")
                    continue

                # ADMIN 사용자로 로그인
                login_response = self.login(admin_user['email'], admin_user['password'])
                if login_response:
                    admin_id = login_response.get('id')

                    # 신청 수락
                    accept_response = self.accept_application(admin_id, application_id)
                    if accept_response:
                        print(f"신청 ID {application_id} 수락 완료: {accept_response}")
                    else:
                        print(f"신청 ID {application_id} 수락 실패")
                else:
                    print(f"ADMIN 로그인 실패: {admin_user['email']}")
