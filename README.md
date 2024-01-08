# DrDictaphone

Dictation app for the terminal and Neovim, using Whisper for transcription and ChatGPT for post-processing.

### Installation

You can use the installation script:
```
curl https://raw.githubusercontent.com/olekli/DrDictaphone/main/script/install.sh | sh
```

Or create a virtual environment and do:
```
pip install drdictaphone
python -m drdictaphone.cli install ~/DrDictaphone
```

Place OpenAI API key in `~/DrDictaphone/config/openai_api_key`.

### Running

To start the standalone app, do `./drdictaphone`.

To start only the server, do `./drdictaphone server`.

Shutdown a running server by doing `./drdictaphone shutdown`.

### Neovim Plugin

If you are not already using Python plugins in Neovim,
you need to create a virtual environment for Neovim to use.
Tell Neovim about it by adding to your `init.vim`:
```
let g:python3_host_prog = '~/.neovim-venv/bin/python'
```
(Or wherever your venv is located.)

Inside this virtual environment, install the Neovim plugin:
```
pip install drdictaphone-neovim-plugin
```

Now you need to add the plugin to your Neovim config directory:
```
ln -s ~/.neovim-venv/lib/python3.11/site-packages/drdictaphone_neovim/DrDictaphone.py ~/.config/nvim/rplugin/python3/.
```
(Your paths may vary.)

Then start the server. Do `:UpdateRemotePlugins` once in Neovim, restart. Use `DrDictaphoneSetProfile`, `DrDictaphoneToggle` vim commands.

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
