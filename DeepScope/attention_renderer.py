class AttentionRenderer:

    def __init__(self):

        self.chars = [
            " ",
            "░",
            "▒",
            "▓",
            "█"
        ]

    def value_to_char(self, value):

        if value < 0.05:
            return " "

        elif value < 0.15:
            return "░"

        elif value < 0.30:
            return "▒"

        elif value < 0.60:
            return "▓"

        else:
            return "█"

    def render(self, matrix):

        for row in matrix:

            line = ""

            for value in row:

                line += self.value_to_char(
                    float(value)
                )

            print(line)