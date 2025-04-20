import os
import random

import click

TEMPLATES = [
    "Связаться с нами можно по телефону {0} или {1}.",
    "Также работает WhatsApp: {2}. Иногда оставляют так: {3}..",
    "А вот и еще: {4}",
    "Звоните по номеру {5} или {6}.",
    "А ещё есть {7} — это второй номер.",
]


def random_phone_components() -> tuple[str, int, int, int, int]:
    """
    Generate a random phone number and return as a tuple.
    """
    prefix = random.choice(["+7", "8"])
    code = random.randint(900, 999)
    a = random.randint(100, 999)
    b = random.randint(10, 99)
    c = random.randint(10, 99)
    return prefix, code, a, b, c


def format_phone(style: int, comps: tuple[str, int, int, int, int]) -> str:
    """
    Get a formatted phone number and return as a string.
    """
    prefix, code, a, b, c = comps
    if style == 1:
        return f"{prefix} {code:03d}-{a:03d}-{b:02d}-{c:02d}"
    if style == 2:
        return f"{prefix} ({code:03d}) {a:03d} {b:02d} {c:02d}"
    if style == 3:
        return f"{prefix}({code:03d}) {a:03d} {b:02d} {c:02d}"
    if style == 4:
        return f"{prefix}-{code:03d}-{a:03d}{b:02d}{c:02d}"
    if style == 5:
        letters = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=4))
        return f"{prefix}{code:03d}{random.randint(1000, 9999)}{letters}"
    if style == 6:
        return f"{prefix} ({code:03d}) {a:03d} {b:02d} {c:02d}"
    if style == 7:
        return f"{prefix}-{code:03d}-{a:03d}-{b:02d}-{c:02d}"

    return f"{prefix} ({code:03d}) {a:03d}.{b:02d}.{c:02d}"


def generate_paragraph() -> str:
    """
    Generates a single paragraph of text with random numbers.
    """
    comps = [random_phone_components() for _ in range(8)]
    nums = [format_phone(i + 1, comps[i]) for i in range(8)]
    lines = [tpl.format(*nums) for tpl in TEMPLATES]
    return "\n".join(lines) + "\n\n"


@click.command()
@click.option(
    "--output", "-o", default="generated.txt", help="Имя выходного файла"
)  # noqa: E501
@click.option(
    "--size-mb", "-s", default=5, type=int, help="Желаемый размер файла в МБ"
)  # noqa: E501
def main(output: str, size_mb: int) -> None:
    """
    Generate text with random numbers.
    """
    target = size_mb * 1024 * 1024
    if os.path.exists(output):
        os.remove(output)
    written = 0
    with open(output, "wb") as f:
        while written < target:
            paragraph = generate_paragraph()
            data = paragraph.encode("utf-8")
            f.write(data)
            written += len(data)
    print(f"Сгенерирован файл '{output}' {written / 1024 / 1024:.2f} МБ")


if __name__ == "__main__":
    main()
