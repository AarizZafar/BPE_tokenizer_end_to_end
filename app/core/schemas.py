from pydantic import BaseModel

class TrainRequest(BaseModel):
    dataset         : str
    vocab_size      : int
    tokenizer_type  : str = "regex"

class EncodeRequest(BaseModel):
    text             : str
    allowed_special : str = "all"

class DecodeRequest(BaseModel):
    ids: list[int]
