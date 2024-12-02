# Introduction

This is a toolkit for automatically creating a Hugging Face repository for a Språkbanken resource. 

# Usage

sb2hf is a command-line tool which creates a Hugging Face repository from a Språkbanken resource url (found at https://spraakbanken.gu.se/resurser). For example, if an authenticated user of the ```sbx`` organization of the user runs this: 

```
python sb2hf.py https://spraakbanken.gu.se/resurser/forarbeten1734 --push-to-hub
```

This dataset with the same resource name will be automatically uploaded: https://huggingface.co/datasets/sbx/forarbeten1734.

To use this outside the Språkbanken Text organization, simply specify your own organization or user under the ``--hf-namespace`` argument.
