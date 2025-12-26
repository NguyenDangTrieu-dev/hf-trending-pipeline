from pydantic import BaseModel
from typing import Optional, List
class SinglePaper(BaseModel):
    title: str
    summary: Optional[str]
    github_link: Optional[str]
    paper_link: str
    published_at: Optional[str]

class PaperList(BaseModel):
    papers: List[SinglePaper]