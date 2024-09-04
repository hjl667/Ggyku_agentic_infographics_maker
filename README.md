# Ggyku - an agentic workflow for making information-heavy minimalistic infographics


## Roadmap
- [ ] refine illustration generation part
- [ ] improve layout
- [ ] add word cloud

## Install
- install miniconda please see https://docs.conda.io/en/latest/miniconda.html
- create a new conda env
```commandline
conda create -n gyaku python=3.11
conda activate gyaku
pip install -r requirements.txt
```

## Basic Usage
- create .env
- provide your open_ai key and mode

```commandline
export OPENAI_KEY = ''
export MODEL = ""
```

- change SAMPLE_PROMPT to your prompt
- run make_infographics

## Design goal:
Given the short attention span of everyone, long-form content, when it's pure text, is very unattractive for people to consume. This is why incorporating visual elements such as infographics, images, and videos into content has become essential. These elements break down complex information into bite-sized, easily digestible pieces, making the content more engaging and accessible. 

## Example

<p align="center">
  <img src="./assets/infographics_sample.png" alt="Project Logo" width="400"/>
</p>

