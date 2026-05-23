import json
import os
from models.linked_list import LinkedList


class BaseRepository:
    """
    Lớp cha cho tất cả repository.
    Mỗi repo con chỉ cần khai báo file_path và model_class.
    """

    file_path = None    # override ở lớp con
    model_class = None  # override ở lớp con

    def __init__(self):
        self._ensure_file()
        self._data = self._load_all()

    # ── I/O cơ bản ────────────────────────────────────────

    def _ensure_file(self):
        """Tạo file JSON rỗng nếu chưa tồn tại."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _load_all(self):
        """Đọc file JSON, trả về LinkedList các object model."""
        with open(self.file_path, "r", encoding="utf-8") as f:
            raw_list = json.load(f)
        linked = LinkedList()
        for item in raw_list:
            linked.append(self.model_class.from_dict(item))
        return linked

    def _save_all(self):
        """Ghi toàn bộ _data xuống file JSON."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(
                [obj.to_dict() for obj in self._data],
                f,
                ensure_ascii=False,
                indent=2,
            )

    # ── Sinh ID tự tăng ───────────────────────────────────

    def _next_id(self):
        max_id = 0
        for obj in self._data:
            if obj.id > max_id:
                max_id = obj.id
        return max_id + 1

    # ── CRUD chung ────────────────────────────────────────

    def get_all(self):
        """Trả về LinkedList toàn bộ bản ghi."""
        return self._data

    def get_by_id(self, id):
        return self._data.find(lambda obj: obj.id == id)

    def add(self, obj):
        obj.id = self._next_id()
        self._data.append(obj)
        self._save_all()
        return obj

    def update(self, id, updated_obj):
        current = self._data.head
        index = 0
        while current is not None:
            if current.data.id == id:
                updated_obj.id = id
                current.data = updated_obj
                self._save_all()
                return updated_obj
            current = current.next
            index += 1
        raise ValueError(f"ID {id} không tồn tại.")

    def delete(self, id):
        current = self._data.head
        index = 0
        while current is not None:
            if current.data.id == id:
                self._data.remove(index)
                self._save_all()
                return True
            current = current.next
            index += 1
        raise ValueError(f"ID {id} không tồn tại.")

    def filter(self, predicate):
        """Lọc theo điều kiện bất kỳ, trả về LinkedList."""
        return self._data.filter(predicate)
