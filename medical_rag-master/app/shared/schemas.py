from pydantic import BaseModel


class ChunkMeta(BaseModel):
    index: int
    file_name: str
    starting_page: int
    end_page: int
    content: str
