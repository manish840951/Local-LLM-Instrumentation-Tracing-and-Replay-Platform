from collections import deque

class TelemetryCollector:

    def __init__(self, max_events=100):   #keeps the capacity constants, older logs are removed

        self.events = deque(maxlen=max_events)

    def add_event(self, event):

        self.events.append(event)

    def get_events(self):

        return list(self.events)
    
latest_metrics = {
    "tokens": 0,
    "entropy": 0.0,
    "attention_mean": 0.0,
    "alerts": [],
    "latency_layers": 0,
    "status": "Waiting"
}

collector = TelemetryCollector()