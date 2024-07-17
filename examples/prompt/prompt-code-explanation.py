"""
Create a custom prompt with variables
"""

from pprint import pprint
import os
from pathlib import Path
# from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials
from genai.schema import DecodingMethod, LengthPenalty, TextGenerationParameters, TextGenerationReturnOptions

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
# load_dotenv()
client = Client(credentials = Credentials(api_key="", api_endpoint=""))


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


prompt_name = "New prompt"
model_id = "ibm/granite-20b-code-instruct"

output_directory_string = "/Users/sujoysett/SUJOY_THINGS/ECLIPSE_WORKSPACE/WatsonX2024CodeExplanation/explanation/"
input_directory_string = "/Users/sujoysett/SUJOY_THINGS/ECLIPSE_WORKSPACE/WatsonX2024CodeExplanation/methods/"
directory = os.fsencode(input_directory_string)

def prompt_llm(code_block):
    total_responses = []
    print(heading("Create prompt"))
    # template = "This is the recipe for {{meal}} as written by {{author}}: "
    template = """Explain the code
```java 
{{code}}
```"""
    create_response = client.prompt.create(
        model_id=model_id,
        name=prompt_name,
        input=template,
        data={"code": code_block},
        parameters=TextGenerationParameters(
            # length_penalty=LengthPenalty(decay_factor=1.5),
            decoding_method=DecodingMethod.GREEDY,
            max_new_tokens= 400,
            min_new_tokens= 100,
            repetition_penalty= 1.0
        ),
    )
    prompt_id = create_response.result.id
    print(f"Prompt id: {prompt_id}")

    print(heading("Get prompt details"))
    retrieve_response = client.prompt.retrieve(id=prompt_id)
    pprint(retrieve_response.result.model_dump())

    print(heading("Generate text using prompt"))
    for generation_response in client.text.generation.create(
        prompt_id=prompt_id,
        parameters=TextGenerationParameters(return_options=TextGenerationReturnOptions(input_text=True)),
    ):
        result = generation_response.results[0]
        print(f"Prompt: {result.input_text}")
        print(f"Answer: {result.generated_text}")
        total_responses.append(result.generated_text)

        print(heading("Delete prompt"))
        client.prompt.delete(id=prompt_id)
        print("OK")
    
    return "\n".join(total_responses)

    # print(heading("Override prompt template variables"))
    # for generation_response in client.text.generation.create(
    #     prompt_id=prompt_id,
    #     parameters=TextGenerationParameters(return_options=TextGenerationReturnOptions(input_text=True)),
    #     data={"meal": "pancakes", "author": "Edgar Allan Poe"},
    # ):
    #     result = generation_response.results[0]
    #     print(f"Prompt: {result.input_text}")
    #     print(f"Answer: {result.generated_text}")

    #     print(heading("Show all existing prompts"))
    #     prompt_list_response = client.prompt.list(search=prompt_name, limit=10, offset=0)
    #     print("Total Count: ", prompt_list_response.total_count)
    #     print("Results: ", prompt_list_response.results)

    #     print(heading("Delete prompt"))
    #     client.prompt.delete(id=prompt_id)
    #     print("OK")

# prompt_llm("""@Override
# public /**
#  * constructs a list of messagedata for enrollment context(list of enrollment ids)
#  */
# List<MessageData> checkEnrollmentStatus(EnrollmentContext enrollmentContext) throws Exception {
#     List<EnrollmentReq> succEnrollmentReqList = getSuccessfulEnrollmentsList(enrollmentContext);
#     if (succEnrollmentReqList != null) {
#         return NotificationUtil.getMessageDataListFromEnrollObjs(succEnrollmentReqList);
#     }
#     return null;
# }""")



inputfiles = os.listdir(directory)
inputfiles.sort()
for file in inputfiles:
    filename = os.fsdecode(file)
    print("Fetched " + filename)
    outputfiles = [os.fsdecode(f) for f in os.listdir(output_directory_string) if os.path.isfile(os.path.join(output_directory_string, f))]

    if filename.endswith(".txt") and filename not in outputfiles:
        print("Processing " + filename)
        output_file = open(output_directory_string + filename , "w")
        output_file.write("")
        output_file.close()
        contents = Path(input_directory_string+filename).read_text()
        print(contents)
        explanation = prompt_llm(contents)
        output_file = open(output_directory_string + filename , "w")
        output_file.write(explanation)
        output_file.close()

        # print(os.path.join(directory, filename))
        continue
    else:
        continue
