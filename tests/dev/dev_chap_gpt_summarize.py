from os import getenv

import openai_summarize
from openai import OpenAI

system_configuration = (
    "You are a GIS (Geographic Information System) specialist with strong skills in "
    "summarizing and explaining technical content to geogeeks. You're alsso a regular "
    "contributor to Geotribu (https://geotribu.fr), a collaborative website about "
    "geomatic and geospatial science. You write your answers in French, Markdown "
    "sometimes decored by emojis."
)


client = OpenAI(
    # This is the default and can be omitted
    api_key=getenv("OPENAI_API_KEY"),
)

# # print(client.models.list())
# for mdl in client.models.list():
#     print(mdl.id)

# print(type(mdl), dir(mdl))


# openai_summarizer = openai_summarize.OpenAISummarize(getenv("OPENAI_API_KEY"))

# text = "This is a long piece of text that needs to be summarized."
# summary = openai_summarizer.summarize_text(text)

# print(summary)

# chat_completion = client.chat.completions.create(
#     messages=[
#         {
#             "role": "user",
#             "content": "Say this is a test",
#         }
#     ],
#     model="gpt-3.5",
# )
# print(chat_completion.)


completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair.",
        },
        {
            "role": "user",
            "content": "Compose a poem that explains the concept of recursion in programming.",
        },
    ],
)

print(completion.choices[0].message)
