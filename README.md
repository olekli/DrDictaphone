# DrDictaphone

Dictation app for the terminal and Neovim, using Whisper for transcription and ChatGPT for post-processing.

### Installation

```
$ mkdir ~/DrDictaphone
$ cd ~/DrDictaphone
$ git clone git@github.com:olekli/DrDictaphone.git app --single-branch
$ cp -r app/profile .
```

Set up environment and install dependencies or simply run `./install`.

Place OpenAI API key in `~/DrDictaphone/config/openai_api_key`.

### Running

To start the standalone app, do `python -m drdictaphone.main` inside the appropriate environment or simply do `./run` inside `app` dir.

To start only the server, do `python -m drdictaphone.server_main` or simply `./run-server`.

### Neovim Plugin

```
$ ln -s ~/DrDictaphone/app/neovim/DrDictaphone.py ~/.config/nvim/rplugin/python3/.
```

Then start the server. Use `DrDictaphoneSetProfile`, `DrDictaphoneToggle` vim commands.

### Controlling Standalone App:

- `s`: select profile
- `p`: start / stop and transcribe recording
- `d`: stop and discard recording
- `q`: exit

### Profiles

Profiles consist of:

- `topic` for transcribing and post-processing, a list of strings
- `language` to use for the transcriber, a string
- `output` directory, a string
- `output_command` to pipe output to
- `enable_vad` whether or not to enable VAD, a bool, defaults to `false`

Output will be written to a timestamped file in the output directory.

VAD will filter recordings for parts with voice before processing them.

### Post-Processor

The Post-Processor specs consist of:

- `instructions` for the post-processor, either a filename to load from or a list of strings
- `gpt_model` to use for post-processing, either a filename to load from or an object
- `options` to use for post-processing, either a filename to load from or an object
- `tools` to use for the post-processor, either a filename to load from or an object

The context for the post-processor is built from the profile and the post-processor specs. Settings in the profile take precedence over settings in the specs.
