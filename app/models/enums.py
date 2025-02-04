from enum import Enum

class UserRole(str, Enum):
    """사용자 역할"""
    ADMIN = "admin"
    USER = "user"

class UserPosition(str, Enum):
    """사용자 직책"""
    STUDENT = "student"          # 학생
    PROFESSOR = "professor"      # 교수
    RESEARCHER = "researcher"    # 연구원
    STAFF = "staff"             # 교직원

class Position(str, Enum):
    """직급 체계"""
    STAFF = "사원"              # 사원
    DEPUTY_MANAGER = "대리"  # 대리
    MANAGER = "과장"          # 과장
    DEPUTY_HEAD = "차장"  # 차장
    HEAD = "부장"                # 부장
    DIRECTOR = "이사"        # 이사
    MANAGING = "상무"        # 상무
    VICE = "전무"                # 전무
    CEO = "대표"                  # 대표



class ReservationStatus(str, Enum):
    """예약 상태"""
    PENDING = "pending"      # 대기 중
    APPROVED = "approved"    # 승인됨
    REJECTED = "rejected"    # 거절됨
    IN_USE = "in_use"       # 사용중
    COMPLETED = "completed"  # 완료됨
    CANCELLED = "cancelled"  # 취소됨