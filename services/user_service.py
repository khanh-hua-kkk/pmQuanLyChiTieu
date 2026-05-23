from models.models import User
from repositories.repositories import UserRepository


def _hash_password(password):
    """Hàm băm tự cài cho mật khẩu.
    Đây là thuật toán đơn giản và xác định, không dùng hashlib.
    """
    if password is None:
        return ""

    salt = "KTLT2026"
    data = (password + salt).encode("utf-8")
    h1 = 0x9e3779b1
    h2 = 0xc3a5c85c

    for b in data:
        h1 = ((h1 << 5) ^ (h1 >> 3) ^ b) & 0xFFFFFFFF
        h2 = ((h2 << 7) ^ (h2 >> 5) ^ (b << 1)) & 0xFFFFFFFF

    result = []
    x = h1 ^ h2
    for i in range(8):
        x = ((x * 0x01000193) ^ (h1 + h2 + i)) & 0xFFFFFFFF
        result.append(f"{x:08x}")

    return "".join(result)


class UserService:
    def __init__(self):
        self.user_repo = UserRepository()

    def register(self, name, email, password, currency="VND"):
        email = email.strip().lower()
        password = password.strip()
        if self.user_repo.get_by_email(email):
            raise ValueError("Email đã được sử dụng.")
        user = User(
            id=0,
            name=name,
            email=email,
            password=_hash_password(password),
            currency=currency,
        )
        return self.user_repo.add(user)

    def login(self, email, password):
        email = email.strip().lower()
        password = password.strip()
        user = self.user_repo.get_by_email(email)
        if user is None or user.password != _hash_password(password):
            raise ValueError("Email hoặc mật khẩu không đúng.")
        return user

    def get_by_id(self, user_id):
        return self.user_repo.get_by_id(user_id)

    def update_profile(self, user_id, **fields):
        user = self.user_repo.get_by_id(user_id)
        if user is None:
            raise ValueError("User không tồn tại.")
        for key, value in fields.items():
            if key == "password":
                value = _hash_password(value)
            if hasattr(user, key):
                setattr(user, key, value)
        return self.user_repo.update(user_id, user)
