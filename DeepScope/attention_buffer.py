from collections import deque

class AttentionBuffer:

    def __init__(self, max_items=100):

        self.buffer = deque(maxlen=max_items)

    def add(self, attention_info):

        self.buffer.append(attention_info)

    def get_all(self):

        return list(self.buffer)