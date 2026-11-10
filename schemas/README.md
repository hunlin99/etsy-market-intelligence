# Research Record v0.1

`research-record.schema.json` uses JSON Schema Draft 2020-12. All fields are explicit; unknown gate states and null decisions are valid. Extra fields are rejected so accidental key typos are visible.

The Python validator additionally checks reference existence, unique IDs, derivation cycles, dates, evidence-backed gates, provenance requirements for policy judgments, and proxy misuse. These checks do not authenticate sources or judge factual entailment.

Start from an appropriate synthetic fixture and replace all example content and provenance with accurately described supplied evidence. See the development guide for commands.
