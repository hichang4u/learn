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