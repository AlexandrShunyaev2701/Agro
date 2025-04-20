import re
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Iterator, List, Optional, Set

import click
from loguru import logger

from constants import A_RE, B_RE, BLOCK_SIZE, C_RE, CODE_RE, PREFIX_RE


class PhoneExtractor:
    """
    Extracts, normalizes, and saves phone numbers
    from a text file using multiprocessing.
    """

    PHONE_RE = re.compile(PREFIX_RE + CODE_RE + A_RE + B_RE + C_RE)

    def __init__(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        workers: Optional[int] = None,
        block_size: int = 4 * 1024 * 1024,
    ) -> None:
        self.input_file = input_file
        self.output_file = output_file
        self.workers = workers
        self.block_size = block_size
        self.seen: Set[str] = set()
        self.result: List[str] = []

    @staticmethod
    def normalize(m: re.Match) -> str:
        """
        Converts a regex Match to a string in the
        format +7(YYY)XXX-XX-XX.
        """
        code, a, b, c = m.group("code", "a", "b", "c")
        return f"+7({code}){a}-{b}-{c}"

    @classmethod
    def process_block(cls, text_block: str) -> List[str]:
        """
        Finds all phone numbers in a block and formats
        them using normalize().
        """
        return [cls.normalize(m) for m in cls.PHONE_RE.finditer(text_block)]

    def generate_blocks(self) -> Iterator[str]:
        """Yields chunks of the input file by lines."""
        tail = ""
        with open(
            self.input_file,
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as f:
            while True:
                chunk = f.read(self.block_size)
                if not chunk:
                    break
                data = tail + chunk
                idx = data.rfind("\n")
                if idx != -1:
                    yield data[: idx + 1]  # noqa: E203
                    tail = data[idx + 1 :]  # noqa: E203
                else:
                    if len(data) > self.block_size * 2:
                        yield data
                        tail = ""
                    else:
                        tail = data
            if tail:
                yield tail

    def parse(self) -> None:
        """
        Process blocks in parallel, filter unique
        numbers, and store results.
        """
        logger.info(
            "Start parsing file {}",
            self.input_file,
        )
        start = time.perf_counter()
        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            for block_nums in executor.map(
                self.process_block,
                self.generate_blocks(),
            ):
                for num in block_nums:
                    if num not in self.seen:
                        self.seen.add(num)
                        self.result.append(num)
        duration = time.perf_counter() - start
        logger.success(
            "Parsing complete: {} unique numbers " "in {:.2f} sec.",
            len(self.result),
            duration,
        )

    def write_output(self) -> None:
        """
        Writes results to file or stdout via click.
        """
        logger.info(
            "Writing {} numbers",
            len(self.result),
        )
        start = time.perf_counter()
        if self.output_file:
            with open(
                self.output_file,
                "w",
                encoding="utf-8",
            ) as f:
                for num in self.result:
                    f.write(num + "\n")
        else:
            for num in self.result:
                click.echo(num)
        duration = time.perf_counter() - start
        logger.success(
            "Write completed in {:.2f} sec.",
            duration,
        )


@click.command()
@click.option(
    "--input",
    "-i",
    "input_file",
    required=True,
    help="Path to the input .txt file",
)
@click.option(
    "--output",
    "-o",
    "output_file",
    default=None,
    help="Where to save results",
)
@click.option(
    "--workers",
    "-w",
    default=None,
    type=int,
    help="Number of processes",
)
def main(
    input_file: str,
    output_file: Optional[str],
    workers: Optional[int],
) -> None:
    """Entry point for phone extraction script."""
    block_size = int(BLOCK_SIZE * 1024 * 1024)
    extractor = PhoneExtractor(
        input_file,
        output_file,
        workers,
        block_size,
    )
    total_start = time.perf_counter()
    extractor.parse()
    extractor.write_output()
    total = time.perf_counter() - total_start
    logger.success(
        "Total time: {:.2f} sec.",
        total,
    )


if __name__ == "__main__":
    main()
