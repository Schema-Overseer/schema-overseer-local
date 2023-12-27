from pydantic import BaseModel


class ApplicationContext(BaseModel):
    my_var: int
