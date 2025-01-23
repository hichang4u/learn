# LEARN: Learning & Education Appointment Reservation Network

## 개요
LEARN은 교육 및 학습 예약을 위한 네트워크 시스템입니다. 이 시스템은 사용자가 교육 세션을 예약하고 관리할 수 있도록 도와줍니다.

## 기술 스택
- **프론트엔드**: Bootstrap, FullCalendar
- **백엔드**: FastAPI
- **데이터베이스**: SQLite

## 설치 및 실행
1. 저장소를 클론합니다.
   ```bash
   git clone <repository-url>
   ```
2. 필요한 패키지를 설치합니다.
   ```bash
   pip install -r requirements.txt
   ```
3. 서버를 실행합니다.
   ```bash
   uvicorn main:app --reload
   ```

## 기능
- 교육 세션 예약
- 일정 관리
- 사용자 인증 및 권한 관리

## 기여
기여를 환영합니다! 이 프로젝트에 기여하려면 다음 단계를 따르세요:
1. 이 저장소를 포크합니다.
2. 기능을 추가하거나 버그를 수정합니다.
3. 변경 사항을 커밋합니다.
4. 풀 리퀘스트를 생성합니다.

## 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다. 

## 관리자 기능
1. **카테고리 관리**: 인프런, 유데미와 같은 카테고리 생성 및 관리.
2. **회원 관리**: 회원 등록, 수정, 삭제 및 권한 관리.
3. **계정 관리**: 각 회원당 1개의 계정 사용 가능 여부 관리.
4. **예약 관리**: 예약 기간(예: 60일 이내) 및 예약 일수(예: 10일 이내) 제약 설정.
5. **통계 및 분석 대시보드**: 계정 사용 통계 및 분석 제공.
6. **회원가입 승인**: 회원가입 요청에 대한 승인 및 관리.

## 사용자 기능
1. **계정 선택**: 사용자가 자신의 계정을 선택할 수 있는 기능.
2. **계정별 일정 현황**: 선택한 계정의 일정 현황 확인.
3. **전체 일정 현황**: 모든 일정의 현황 확인.
4. **일정 추가/수정/삭제**: 일정 관리 기능.
5. **신청 및 승인**: 일정 신청 및 승인 절차.
6. **알림 시스템**: 신청자 및 승인자에 대한 알림 제공.
7. **Q&A와 공지사항**: 질문과 답변, 공지사항 확인 및 참여.
8. **회원가입 및 로그인**: 사용자 계정 생성 및 로그인 기능. 

/project-root
│
├── /app
│   ├── /api
│   │   ├── __init__.py
│   │   ├── endpoints.py
│   │   └── models.py
│   ├── /core
│   │   ├── __init__.py
│   │   └── config.py
│   ├── /db
│   │   ├── __init__.py
│   │   └── database.py
│   ├── /schemas
│   │   ├── __init__.py
│   │   └── user.py
│   ├── /services
│   │   ├── __init__.py
│   │   └── user_service.py
│   └── main.py
│
├── /frontend
│   ├── /static
│   │   ├── /css
│   │   └── /js
│   ├── /templates
│   │   └── index.html
│   └── app.js
│
├── /migrations
│   └── alembic.ini
│
├── /tests
│   ├── test_main.py
│   └── test_endpoints.py
│
├── .gitignore
├── README.md
├── requirements.txt
└── setup.py