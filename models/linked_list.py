class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def append(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next is not None:
                current = current.next
            current.next = new_node
        self.size += 1

    def get(self, index):
        if index < 0 or index >= self.size:
            raise IndexError("Index out of range")
        current = self.head
        for _ in range(index):
            current = current.next
        return current.data

    def remove(self, index):
        if index < 0 or index >= self.size:
            raise IndexError("Index out of range")
        if index == 0:
            self.head = self.head.next
        else:
            current = self.head
            for _ in range(index - 1):
                current = current.next
            current.next = current.next.next
        self.size -= 1

    def find(self, predicate):
        """Tìm phần tử đầu tiên thỏa điều kiện predicate(data) == True"""
        current = self.head
        while current is not None:
            if predicate(current.data):
                return current.data
            current = current.next
        return None

    def filter(self, predicate):
        """Trả về LinkedList mới chứa các phần tử thỏa điều kiện"""
        result = LinkedList()
        current = self.head
        while current is not None:
            if predicate(current.data):
                result.append(current.data)
            current = current.next
        return result

    def to_list(self):
        """Chuyển sang Python list thông thường (chỉ dùng khi cần JSON)"""
        result = []
        current = self.head
        while current is not None:
            result.append(current.data)
            current = current.next
        return result

    def __iter__(self):
        current = self.head
        while current is not None:
            yield current.data
            current = current.next

    def __len__(self):
        return self.size

    def __repr__(self):
        return f"LinkedList(size={self.size})"
