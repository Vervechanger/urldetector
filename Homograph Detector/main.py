from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from homograph_core import scan_text, scan_domain

class RootWidget(BoxLayout):
    def scan_input_text(self):
        text = self.ids.input_box.text
        results = scan_text(text)
        self.show_results(results)

    def scan_input_url(self):
        url = self.ids.input_box.text
        results = scan_domain(url)
        self.show_results(results)

    def show_results(self, results):
        if not results:
            self.ids.output_box.text = "✅ All characters are safe and standard."
            return
        lines = ["⚠️ Suspicious characters found:\n"]
        for ch, name, codepoint in results:
            display = repr(ch) if ch.isspace() else ch
            lines.append(f"{display} — {name} ({codepoint})")
        self.ids.output_box.text = "\n".join(lines)

class HomographApp(App):
    def build(self):
        return RootWidget()
