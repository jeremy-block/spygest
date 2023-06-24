# Prompt Engineering for Summarization

## Configuration

## User

## Document

## Preprocessing

- The process of converting interaction logs to interaction sentences is implemented in [another part](../data_prep_scripts/06-Rule_Based_Sentence_Generator%26Hugging_Face_Summarizers.ipynb) of the repository
  - We are planning to integrate that process into this package
- Call functions implemented in the document module to extract summaries, topics, and entities

## Summarization

## Post Processing

- generate samples for the entire interaction session in the format of {"summary": summary, "article": article} for checking factuality using FactGraph.