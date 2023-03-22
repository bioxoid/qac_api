from pydantic import BaseModel

class Star(BaseModel):
    """Type definition of stars used in stars.json."""

    id: int
    mag: float
    size: int
    x: float
    y: float
    z: float
    r: int
    g: int
    b: int


class QAArgs(BaseModel):
    """Type definition of quantum annealing arguments."""

    token: str
    lagrange_multiplier: float
    num_reads: int
