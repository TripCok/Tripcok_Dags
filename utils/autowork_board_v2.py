import random
from faker import Faker
import mysql.connector
import requests

class AutoWorkBoard:
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

    # 1. 로그인
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

            response = self.session.put(self.api + '/member/login', json={'email': email, 'password': password})

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

    # 2. 가입된 모임 목록 확인
    def get_my_groups(self):
        response = self.session.get(self.api + '/group/my', params={'memberId': self.member_id})
        if response.status_code == 200:
            groups_response = response.json()
            groups = groups_response.get('content', [])
            print("가입된 모임 목록:")
            for group in groups:
                print(f"- {group.get('groupName', '이름 없음')} (ID: {group.get('id')})")
            return groups
        else:
            print(f"모임 목록 조회 실패: {response.status_code}, {response.text}")
            return []

    # 3. 내 모임 중 랜덤으로 선택
    def choose_random_group(self):
        groups = self.get_my_groups()
        if not groups:
            print("가입된 모임이 없습니다.")
            return None
        chosen_group = random.choice(groups)
        print(f"선택된 모임: {chosen_group}")
        return chosen_group

    # 4. 선택된 모임의 게시판 확인
    def get_group_board(self, group_id):
        response = self.session.get(self.api + '/posts', params={'groupId': group_id})
        if response.status_code == 200:
            posts = response.json().get('posts', [])
            print(f"모임 게시판 글 목록: {posts}")
            return posts
        else:
            print(f"게시판 조회 실패: {response.status_code}, {response.text}")
            return []

    def generate_random_text(self):
        title = " ".join([self.fake.catch_phrase() for _ in range(1)])
        content = " ".join([self.fake.catch_phrase() for _ in range(5)])
        return title, content

    def generate_random_comment(self):
        return " ".join([self.fake.catch_phrase() for _ in range(2)])

    # 5. 게시판에 글 작성
    def create_travel_post(self, group_id):
        title, content = self.generate_random_text()
        post_data = {
            "title": title,
            "content": content,
            "type": "COMMON"
        }
        params = {"memberId": self.member_id, "groupId": group_id}
        response = self.session.post(self.api + '/group/post', params=params, json=post_data)
        if response.status_code == 201:
            print(f"여행 계획 글 작성 완료: {response.json()}")
            return {"postId": response.json().get("postId"), "title": title, "content": content}
        else:
            print(f"여행 계획 글 작성 실패: {response.status_code}, {response.text}")
            return None

    # 6. 게시판 상태 업데이트
    def update_board_with_new_posts(self, group_id, new_posts):
        board_posts = self.get_group_board(group_id)
        if board_posts:
            board_posts.extend(new_posts)
        else:
            board_posts = new_posts
        return board_posts

    # 7. 게시판 글에 댓글 작성
    def post_comment(self, post_id, group_id, content=None):
        if content is None:
            content = self.generate_random_comment()

        comment_data = {
            "memberId": self.member_id,
            "groupId": group_id,
            "postId": post_id,
            "content": content
        }

        response = self.session.post(self.api + '/postComment', json=comment_data)
        if response.status_code == 201:
            print(f"댓글 작성 완료: {response.json()}")
            return {"commentId": response.json().get("postId"), "content": content}
        else:
            print(f"댓글 작성 실패: {response.status_code}, {response.text}")
            return None

    # 전체 실행
    def run_scenario(self):
        print("==시나리오 시작==")

        # 1. 로그인
        login_response = self.login()
        if not login_response:
            print("로그인 실패: 프로세스를 중단합니다.")
            return

        # 2. 가입된 모임 목록 확인
        groups = self.get_my_groups()
        if not groups:
            print("가입된 모임이 없습니다. 시나리오를 종료합니다.")
            return

        # 3. 랜덤 모임 선택
        chosen_group = self.choose_random_group()
        if not chosen_group:
            print("모임 선택 실패. 시나리오를 종료합니다.")
            return

        group_id = chosen_group.get('id')

        # 4. 게시판 확인 및 글 작성
        board_posts = self.get_group_board(group_id)
        new_posts = []
        if not board_posts:
            print("게시판에 글이 없습니다. 여행 계획 글을 작성합니다.")
            for _ in range(random.randint(1, 3)):
                new_post = self.create_travel_post(group_id)
                if new_post:
                    new_posts.append(new_post)

        board_posts = self.update_board_with_new_posts(group_id, new_posts)

        # 5. 댓글 작성
        for post in board_posts:
            if random.choice([True, False]):
                self.post_comment(post.get('postId'), group_id)

        print("==시나리오 종료==")
