# Document Vector Search Server Sample

This is a lightweight vector search server sample that populates a chroma database from a set of \*.json files in a folder and provides an endpoint to search for document ids and scores based on query text.

You will need an API key from an OpenAI Project to be set in the OPENAI_API_KEY environment variable or added to the code.

Run with *fastapi run sbert_server.py*

## Control Properties

These properties control where files used in the load process are read from and how to index them in Chroma:

**path** The path to the folder containing 1 or more json files to be processed. The files should contain an array of objects, like [{"id": "abc", "text": "descriptive text", "other": "ignored content"},{"id": "123", "text": "descriptive text"}, ...]
**packet_size** The number of documents in a batch to push into the Chroma db.
**max_docs** The maximum number of documents to load into the Chroma db. A value of "0" indicates all documents found in the **path** should be processed.
**id_field** The name of the input field where a unique id for a document is located. It does not have to be the "id" field. It will be returned in the "id" property on a query. If the unique id is already a string value, the code will need to be adjusted to remove str() conversion functions.
**text_field** The name of the input field where the text to be processed through the LLM is located. This will likely be a "name" field. It is translated to a vector location in the Chroma db.

## Endpoints

**GET /load** Runs the load process. This will empty the Chroma db if it already has content and repopulate it based on the \*.json files

**GET /query?q={query text}&count={k}** Where query text is the text to match documents to and k is the number of documents to return. The response will be a JSON object that looks like:
> [<br>
> {<br>
> 	id: The id of the document,<br>
>   score: a double representing the similarity score for the id<br>
> },<br>
> {<br>
> 	id: 'abc',<br>
>   score: 0.96312<br>
> },<br>
> . . .<br>
> ]

**GET /doc?doc_id={doc id}** Retrieves details for the specified doc id
