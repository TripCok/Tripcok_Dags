# Airflow Dags

## Airflow 기반 자동화 워크플로

Tripcok DAGs는 **사용자 등록**, **로그인**, **모임 생성 및 신청** 등의 워크플로를 Airflow로 자동화하여 Tripcok 데이터베이스에 데이터를 적재하는 데 사용됩니다. 이 DAG는 Tripcok 플랫폼의 운영 데이터 시뮬레이션 및 테스트 데이터 생성을 목적으로 합니다.

---

## 주요 기능

1. **사용자 자동 등록 및 로그인**
    - 회원가입 및 로그인 과정을 자동화합니다.
    - 선호 카테고리를 설정합니다.

2. **모임 생성 및 관리**
    - 로그인한 사용자가 모임을 생성합니다.
    - 사용자가 다른 모임에 랜덤으로 가입 신청을 합니다.

3. **모임 신청 관리**
    - ADMIN 권한을 가진 사용자가 신청을 승인합니다.

4. **게시판 시나리오 처리**
    - 게시판 관련 커스텀 작업을 실행합니다.

---

## DAG 워크플로 구성

### DAG 정보

- **DAG ID**: `auto_work_dag`
- **실행 주기**: 매 5분 실행 (`*/5 * * * *`)
- **태그**: `['auto', 'ingest', 'log', 'data', 'work']`

### DAG 작업

1. **`auto_work_register_login_task`**
    - 사용자 회원가입 및 선호 카테고리 설정을 자동화합니다.

2. **`auto_work_group_task`**
    - 모임을 생성하고 관련 작업을 실행합니다.

3. **`auto_work_group_join_task`**
    - 다른 모임에 참여 신청을 하고, 신청을 승인합니다.

4. **`auto_work_board_task`**
    - 게시판 관련 작업을 처리합니다.

---


### REQUIRED IMPL
```
pip install mysql-connector-python==9.1.0 \
Faker==33.1.0
```