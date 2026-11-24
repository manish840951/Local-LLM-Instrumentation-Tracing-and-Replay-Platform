from textual.app import App
from textual.containers import Vertical
from textual.widgets import Header, Footer
from dashboard import Dashboard
import os
import json
from textual.widgets import Header, Footer, Static



class DeepScopeUI(App):
    selected_event_index = -1
    selected_head = 0
    selected_replay_index = -1
    selected_layer = 0
   
    CSS = """

    
    #model_info {
        width: 40%;
        height: 12;
        border: solid green;
        padding: 1;
    }

    #packet_stream {
        width: 60%;
        height: 12;
        border: solid cyan;
        padding: 1;
    }

    #attention {
        width: 60%;
        height: 13;
        border: solid magenta;
        padding: 1;
    }
    #attention_controls {
        width: 15%;
        height: 13;
        border: solid white;
        padding: 1;
    }
    #replay {
        width: 25%;
        height: 13;
        border: solid yellow;
        padding: 1;
    }
    #telemetry {
        width: 45%;
        height: 20;
        border: solid blue;
        padding: 1;
    }

    #alerts {
        width: 55%;
        height: 15;
        border: solid red;
        padding: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        # ("f", "next_panel", "Next Panel"),
        ("j", "next_event", "Next Event"),
        ("k", "previous_event", "Previous Event"),
        ("h", "previous_head", "Previous Head"),
        ("l", "next_head", "Next Head"),
        ("p", "next_replay", "Next Replay"),
        ("u", "previous_layer", "Previous Layer"),
        ("i", "next_layer", "Next Layer"),
    ]

    def action_next_head(self):
        metrics = self.load_metrics()
        heads = metrics.get("attention_heads", [])

        if heads:
            self.selected_head = min(
                self.selected_head + 1,
                len(heads) - 1
            )

        self.refresh_dashboard()

    def action_next_event(self):
        metrics = self.load_metrics()
        events = metrics.get("events", [])

        if events:
            visible_start = max(0, len(events) - 10)
            visible_end = len(events) - 1

            if self.selected_event_index == -1:
                self.selected_event_index = visible_start
            else:
                self.selected_event_index = min(
                    self.selected_event_index + 1,
                    visible_end
                )

        self.refresh_dashboard()

    def action_previous_head(self):
        if self.selected_head > 0:
            self.selected_head -= 1

        self.refresh_dashboard()

    def action_previous_event(self):
        metrics = self.load_metrics()
        events = metrics.get("events", [])

        if events:
            visible_start = max(0, len(events) - 10)

            if self.selected_event_index == -1:
                self.selected_event_index = len(events) - 1
            else:
                self.selected_event_index = max(
                    self.selected_event_index - 1,
                    visible_start
                )

        self.refresh_dashboard()

    def action_next_replay(self):
        metrics = self.load_metrics()

        replays = metrics.get("available_replays", [])

        if not replays:
            return

        self.selected_replay_index = (
            self.selected_replay_index + 1
        ) % len(replays)

        self.refresh_dashboard()


    def action_next_layer(self):
        metrics = self.load_metrics()
        layers = metrics.get("attention_layers", [])

        if layers:
            self.selected_layer = min(
                self.selected_layer + 1,
                len(layers) - 1
            )

        self.refresh_dashboard()


    def action_previous_layer(self):
        if self.selected_layer > 0:
            self.selected_layer -= 1

        self.refresh_dashboard()


    def compose(self):
        
        with Vertical():
            yield Dashboard()

        yield Footer()

    def on_mount(self):
        self.set_interval(1, self.refresh_dashboard)

    def action_refresh(self):
        self.refresh_dashboard()

    def load_metrics(self):

        metrics_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "metrics.json"
        )

        default_metrics = {
            "tokens": 0,
            "attention_mean": 0.0,
            "latency_layers": 0,
            "alerts": [],
            "status": "Waiting"
        }

        try:
            with open(metrics_path, "r") as f:
                return json.load(f)

        except Exception:
            return default_metrics

    def short_layer_name(self, layer):

        return (
            layer
            .replace("transformer.", "")
            .replace("attn.", "")
            .replace("mlp.", "")
        )

    def refresh_dashboard(self):

        metrics = self.load_metrics()
        model_info = self.query_one("#model_info")
        tree = metrics.get("topology", {})

        # text = self.panel_title(0, "1. MODEL TOPOLOGY") + "\n\n"
        events = metrics.get("events", [])
        selected_block = self.selected_layer

        text = "1. MODEL TOPOLOGY\n\n"
        text += "▼ gpt2\n"
        text += "  ► embeddings\n"
        text += "  ▼ transformer blocks\n"

        total_layers = metrics.get("model", {}).get("layers", 12)

        if isinstance(selected_block, int) and selected_block >= 0:
            start_layer = max(0, selected_block - 2)
        else:
            start_layer = 0
        end_layer = min(total_layers, start_layer + 5)

        for i in range(start_layer, end_layer):
            marker = "●" if i == selected_block else "►"
            active = "  [Active Capture Target]" if i == selected_block else ""
            text += f"    {marker} layer.{i}{active}\n"
        text += "  ► ln_f\n"
        text += "  ► lm_head\n"

        model_info.update(text)
        

        packet_stream = self.query_one("#packet_stream")
        events = metrics.get("events", [])

        if events and self.selected_event_index == -1:
            self.selected_event_index = len(events) - 1

        packet_text = (
            "2. LIVE PACKET STREAM\n\n"
            " ID   TIME        TYPE        DEVICE      LATENCY\n"
            "-----------------------------------------------------\n"
        )

        if events:
            window_size = 6
            start = max(0, self.selected_event_index - window_size // 2)
            end = min(len(events), start + window_size)

            visible_events = events[start:end]

            for i, event in enumerate(visible_events):
                global_index = start + i
                pointer = "▶" if global_index == self.selected_event_index else " "

                packet_text += (
                    f"{pointer}"
                    f"{global_index:>3}  "
                    f"{event.get('timestamp', '--:--:--'):>10}  "
                    f"{event.get('layer_type', 'OTHER')[:9]:<11}"
                    f"{event.get('device', 'CPU')[:10]:<12}"
                    f"{event.get('latency_ms', 0):6.3f} ms\n"
                )
        else:
            packet_text += (
                f"{pointer} "
                f"{global_index:<3}| "
                f"{event.get('timestamp', '--:--:--'):<8} | "
                f"{event.get('layer_type', 'OTHER'):<10} | "
                f"B{event.get('block', '-'):<4} | "
                f"{event.get('device', '-')}\n"
            )
        packet_stream.update(packet_text)

        attention = self.query_one("#attention")
        attention_layers = metrics.get("attention_layers", [])

        if attention_layers:

            self.selected_layer = min(
                self.selected_layer,
                len(attention_layers) - 1
            )

            attention_heads = attention_layers[self.selected_layer]

            self.selected_head = min(
                self.selected_head,
                len(attention_heads) - 1
            )

            matrix = attention_heads[self.selected_head]

        else:
            matrix = metrics.get("attention_matrix", [])
                
        tokens = metrics.get("token_labels", [])
        layer = self.selected_layer
        head = self.selected_head

        chars = [" ", "░", "▒", "▓", "█"]

        def val_to_char(v):
            if v < 0.05:
                return chars[0]
            elif v < 0.15:
                return chars[1]
            elif v < 0.30:
                return chars[2]
            elif v < 0.60:
                return chars[3]
            return chars[4]

        # text = f"ATTENTION MATRIX VISUALIZER | Layer {layer}, Head {head}\n\n"
        num_layers = len(attention_layers)
        num_heads = len(attention_heads)

        text = (
            "3. ATTENTION MATRIX VISUALIZER\n"
            f"Layer {layer+1}/{num_layers}    "
            f"Head {head+1}/{num_heads}\n\n"
        )
        if matrix:
            # short_tokens = [t.replace("Ġ", "")[:6] for t in tokens[:8]]
            def clean_token(t):
                t = (
                    t.replace("\u0120", "")
                    .replace("\u010a", "<NL>")
                    .replace("\u0109", "<TAB>")
                )

                if t == "":
                    return "·"

                return t[:7]

            short_tokens = [clean_token(t) for t in tokens[:8]]

            # text += "Tokens: "
            text += " ".join(f"<{t}>" for t in short_tokens[:8])
            text += "\n\n"

            show_n = min(4, len(short_tokens), len(matrix))

            text += "          "
            for token in short_tokens[:show_n]:
                text += f"{token[:5]:<7}"
            text += "\n"

            for i, row in enumerate(matrix[:show_n]):
                label = short_tokens[i] if i < len(short_tokens) else str(i)
                line = f"{label[:8]:<10}"

                for value in row[:show_n]:
                    line += f"{val_to_char(float(value)) * 2:<7}"

                text += line + "\n"

                
        attention.update(text)
        attention_controls = self.query_one("#attention_controls")

        control_text = (
            "MATRIX CONTROLS\n\n"
            "h/l  Change Head\n"
            "u/i  Change Layer\n"
            "j/k  Select Event\n"
            "p    Next Replay\n"
            "r    Refresh\n"
            "q    Quit\n"
        )

        attention_controls.update(control_text)
        replay_panel = self.query_one("#replay")

        replays = metrics.get("available_replays", [])

        replay_text = "REPLAY HISTORY\n\n"

        if replays:
            recent_replays = replays[-6:]

            for i, replay in enumerate(recent_replays):
                real_index = len(replays) - len(recent_replays) + i
                pointer = ">" if real_index == self.selected_replay_index else " "
                replay_text += f"{pointer} {replay}\n"
        else:
            replay_text += "No replay files yet"

        replay_panel.update(replay_text)

        telemetry = self.query_one("#telemetry")

        # telemetry = self.query_one("#telemetry")

        events = metrics.get("events", [])

        if events:

            if self.selected_event_index == -1:
                self.selected_event_index = len(events) - 1

            self.selected_event_index = max(
                0,
                min(self.selected_event_index, len(events) - 1)
            )

            latest_event = events[self.selected_event_index]

        else:
            latest_event = {}

        # replays = metrics.get("available_replays", [])
        # recent_replays = replays[-3:]

        replays = metrics.get("available_replays", [])
        recent_replays = replays[-1]

        replay_text = ""

        for i, replay in enumerate(recent_replays):
            real_index = len(replays) - len(recent_replays) + i
            pointer = ">" if real_index == self.selected_replay_index else " "
            replay_text += f"{pointer} {replay}\n"

        # print(latest_event)


        sparsity = latest_event.get("sparsity", 0)
        filled = int(sparsity * 10)
        empty = 10 - filled
        sparsity_bar = "█" * filled + "░" * empty


        telemetry.update(
            f"""
        4. RUNTIME METRICS INSPECTOR

        TensorShape : {latest_event.get('shape', '-')}
        Dtype        : {latest_event.get('dtype', '-')}
        Device       : {latest_event.get('device', '-')}
        Layer Type   : {latest_event.get('layer_type', '-')}
        Block        : {latest_event.get('block', '-')}
        Latency      : {latest_event.get('latency_ms', 0):.4f} ms
        Sparsity Rate: {sparsity_bar} {sparsity * 100:.1f}%
        Mean         : {latest_event.get('mean', 0):.4f}
        Max          : {latest_event.get('max', 0):.4f}
        Std          : {latest_event.get('std', 0):.4f}
        """
        )
        # telemetry.update(
        #     f"""
        # RUNTIME METRICS

        # Tokens          : {metrics.get('tokens', 0)}
        # Attention Mean  : {metrics.get('attention_mean', 0):.6f}
        # Latency Layers  : {metrics.get('latency_layers', 0)}
        # Status          : {metrics.get('status', 'Waiting')}

        # SELECTED LAYER

        # Layer Type      : {latest_event.get('layer_type', '-')}
        # Block           : {latest_event.get('block', '-')}
        # Shape           : {latest_event.get('shape', '-')}
        # Dtype           : {latest_event.get('dtype', '-')}
        # Device          : {latest_event.get('device', '-')}
        # Latency         : {latest_event.get('latency_ms', 0):.4f} ms
        # Sparsity        : {latest_event.get('sparsity', 0):.4f}
        # Mean            : {latest_event.get('mean', 0):.4f}
        # Max             : {latest_event.get('max', 0):.4f}
        # Std             : {latest_event.get('std', 0):.4f}

        # REPLAYS

        # {replay_text if replay_text else "No replay files yet"}
        # """

        
        # )

        alerts = self.query_one("#alerts")
        alert_list = metrics.get("alerts", [])

        if not alert_list:
            alerts.update("ANOMALY LEDGER\n\nNo alerts")
            return

        alert_text = "5. NUMERICAL ANOMALY LEDGER\n\n"

        for alert in alert_list[:5]:
            severity = alert.get("severity", "INFO")
            layer = self.short_layer_name(alert.get("layer", "unknown"))
            message = alert.get("message", "")
            value = alert.get("value", "")

            if severity in ["WARN", "WARNING"]:
                icon = "!"
            elif severity == "ERROR":
                icon = "X"
            else:
                icon = "."

            alert_text += (
                f"{icon} {severity}\n"
                f"Layer : {layer}\n"
                f"{message}\n"
            )

            if value != "":
                alert_text += f"Value : {value}\n"

            alert_text += "\n"

        alerts.update(alert_text)

if __name__ == "__main__":
    DeepScopeUI().run()


# from textual.app import App
# from textual.containers import Vertical
# from textual.widgets import Header
# from textual.widgets import Footer
# from textual.widgets import Log
# from dashboard import Dashboard
# import sys
# import os
# import json

# sys.path.append(
#     os.path.dirname(
#         os.path.dirname(__file__)
#     )
# )

# from telemetry_collector import latest_metrics



# class DeepScopeUI(App):

#     CSS = """
#     #model_info {
#         width: 30%;
#         border: solid green;
#     }

#     #telemetry {
#         width: 40%;
#         border: solid blue;
#     }

#     #alerts {
#         width: 30%;
#         border: solid red;
#     }
#     """

#     def compose(self):

#         yield Header()

#         with Vertical():

#             yield Dashboard()

#             yield Log()

#         yield Footer()

#     def on_mount(self):

#         self.set_interval(
#             1,
#             self.refresh_dashboard
#         )

#     def refresh_dashboard(self):
#         import os

        
#         metrics_path = os.path.join(
#             os.path.dirname(os.path.dirname(__file__)),
#                 "metrics.json"
#         )
#         try:
#             with open(metrics_path, "r") as f:
#                 latest_metrics.update(json.load(f))

#         except Exception as e:
#             print("Metrics read error:", e)
#         telemetry = self.query_one("#telemetry")

#         telemetry.update(
#             f"""
#     Tokens: {latest_metrics['tokens']}

#     Entropy:
#     {latest_metrics['entropy']:.4f}

#     Attention Mean:
#     {latest_metrics['attention_mean']:.4f}

#     Latency Layers:
#     {latest_metrics['latency_layers']}

#     Status:
#     {latest_metrics['status']}
#     """
#         )

#         alerts = self.query_one("#alerts")

#         if latest_metrics["alerts"]:
#             alert_text = ""

#             for alert in latest_metrics["alerts"][:5]:

#                 layer = alert["layer"]

#                 layer = (
#                     layer
#                     .replace("transformer.", "")
#                     .replace("mlp.", "")
#                     .replace("attn.", "")
#                 )

#                 value = alert.get("value", "")

#                 alert_text += (
#                     f"[{alert['severity']}]\n"
#                     f"{layer}\n"
#                     f"{value}\n\n"
#                 )

#             alerts.update(alert_text)
#         else:
#             alerts.update("No alerts")
    


# if __name__ == "__main__":
#     DeepScopeUI().run()