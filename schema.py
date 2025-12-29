from pydantic import BaseModel
from typing import Optional, List
class SinglePaper(BaseModel):
    title: str
    summary: Optional[str] | None
    github_link: Optional[str] | None
    paper_link: str|None
    published_at: Optional[str]

class PaperList(BaseModel):
    papers: List[SinglePaper]