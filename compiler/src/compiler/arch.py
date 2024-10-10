from enum import Enum


class Arch(str, Enum):
    x86_64 = "x86_64"
    aarch64 = "aarch64"

