"""Keep track of the hash of files and summaries to prevent needless updates."""

from hashlib import md5
from json import dump, load
from pathlib import Path


class HashRegister:
    """Keep track of changes to input-output pairs."""

    def __init__(self, hashes: dict[str, tuple[str, str]]) -> None:
        self.hashes = hashes

    def set(self, key: str, input: str, output: str) -> None:
        """Register the pair."""
        self.hashes[key] = (self._hash(input), output)

    def get(self, key) -> str:
        """Return the output for the key."""
        return self.hashes[key][1]

    def is_changed(self, key: str, input: str) -> bool:
        """Return whether the input changed."""
        if key not in self.hashes:
            return True
        return self._hash(input) != self.hashes[key][0]

    @staticmethod
    def _hash(input: str) -> str:
        """Create a hash for the input value."""
        return md5(input.encode("utf-8"), usedforsecurity=False).hexdigest()


def load_hashes(file_path: Path) -> HashRegister:
    """Load the hashes."""
    if file_path.exists():
        with file_path.open() as fd:
            hashes = load(fd)
    else:
        hashes = {}
    return HashRegister(hashes)


def save_hashes(file_path: Path, hash_register: HashRegister) -> None:
    """Save the hashes."""
    with file_path.open("w") as fd:
        dump(hash_register.hashes, fd)
