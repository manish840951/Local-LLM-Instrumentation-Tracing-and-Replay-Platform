from textual.containers import Horizontal, Vertical
from textual.widgets import Static


class Dashboard(Vertical):

    def compose(self):

        with Horizontal():
            yield Static("MODEL TOPOLOGY\n\nGPT-2\n├── embeddings\n├── transformer blocks\n└── lm_head", id="model_info")
            yield Static("LIVE PACKET STREAM\n\nWaiting for backend trace export...", id="packet_stream")

        # yield Static("ATTENTION MATRIX VISUALIZER\n\nBackend currently exports only attention_mean.\nFull matrix view will be added later.", id="attention")
        with Horizontal():
            yield Static(
                "ATTENTION MATRIX VISUALIZER",
                id="attention"
            )
            yield Static(
                "MATRIX CONTROLS",
                id="attention_controls"
            )
            yield Static(
                "REPLAY HISTORY",
                id="replay"
            )
        with Horizontal():
            yield Static("RUNTIME METRICS", id="telemetry")
            yield Static("ANOMALY LEDGER", id="alerts")

# from textual.containers import Horizontal
# from textual.widgets import Static


# class Dashboard(Horizontal):

#     def compose(self):

#         yield Static(
#         """
#         Model: GPT-2

#         Layers: 12

#         Heads: 12

#         Parameters: 124M
#         """,
#         id="model_info"
#         )

#         yield Static(
#             "Telemetry",
#             id="telemetry"
#         )

#         yield Static(
#             "Alerts",
#             id="alerts"
#         )