# Prompt Engineering for Summarization

This package includes several modules to enable our prompt engineering experiment

## Configuration

- This TOML file is used to specify hyperparameters and independent variables, including the prompts for:
  - Audiences
  - Examples

## User

- This module is implemented to store data that is specific to a user
- Interaction sentences are read from preprocessed files and appended to a list as a `User` class attribute

## Document

- This module implements functions to send requests to the OpenAI Chat Completions API for extracting information from documents
  - `summarize()`: gets a short summary of each document in at most 100 words
  - `get_topics()`: gets a certain number of topics and returns a list of topics separated by commas
  - `get_entities()`: gets specified types of entities and returns them in the JSON format

## Utils

- This module implements common utility functions, including functions that:
  - Send requests to the OpenAI Chat Completions API and returns the response
  - Count the number of tokens of a given `messages` list
  - Write to and read from JSON files
  - Compare text and highlight the different part

## Preprocessing

- The process of converting interaction logs to interaction sentences is implemented in [another part](../data_prep_scripts/01-Rule_Based_Sentence_Generator.ipynb) of the repository
  - We are planning to integrate that process into this package
- Call functions implemented in the document module to extract summaries, topics, and entities

## Prompt: Summarization via Prompting

- This is the module that implements the main pipeline of our experiment
- The system and user messages (both segment and final, please refer to the paper for the difference between these two user messages) are structured in this module using the functions:
  - `get_system_message()`
  - `get_user_message()`
  - `get_user_message_final()`
- Our recursive prompting technique is implemented inside the main function,
  - To address the model's "memory-less" nature, we utilize a `context` (this is referred to as "messages" in the paper) list to accumulate sent messages and responses, in order to provide ChatGPT with contextual information.
  - The list begins with a system message, followed by a user message containing an instructional line and the corresponding segment logs.
  - The `context` list is then sent as API requests to ChatGPT, and an assistant message, generated from the API response, is appended to the list, enabling the inclusion of previous segment summaries for context in subsequent requests.
  - The entire list is sent to the API in each request, and the list keeps growing as we add all sent messages and responses to it.

## Post Processing

- This module implements functions that generate samples for the entire interaction session in the format of {"summary": summary, "article": article} for checking factuality using FactGraph.
- The FactGraph methods return incorrect for all of our summaries.
- As described in the paper, we use FRANK as an alternative to manually calculate a Factuality value.

## Snapshots: P1, P2, P3

- These are the folders that contain snapshots of all the intermediate results
