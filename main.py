from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.clock_window import ClockWindow


def main() -> None:
    application = QApplication(sys.argv)

    window = ClockWindow()
    window.show()

    sys.exit(application.exec())


if __name__ == "__main__":
    main()