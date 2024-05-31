from openai import OpenAI
from registry import registry


class gepetto:
    R=None
    msg=[]
    client=None
    def __init__(self):
        self.R = registry.Instance()
        self.client=OpenAI(
            api_key=self.R.cfg['openai']
        )
        self.msg.append({"role": "system", "content":self.R.aipers})
    pass

    def askGepetto(self, txt):
        self.msg.append({"role":"user","content":txt})
        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.msg,
                max_tokens=128
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(e)
            return self.R.t['aierr']



