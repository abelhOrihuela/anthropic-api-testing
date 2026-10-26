import voyageai
from dotenv import load_dotenv


class VoyageApi:

    def __init__(self, model="voyage-3-large"):
        load_dotenv()
        self.model = model
        self.client = voyageai.Client()

    def generate_embedding(self, text, input_type="query"):
        result = self.client.embed([text], model=self.model, input_type=input_type)
        return result.embeddings[0]
