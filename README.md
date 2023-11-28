# DrDictaphone

Dictation app for the terminal, using Whisper for transcription and ChatGPT for post-processing.

### Running

```
$ mkdir config
$ echo 'YOUR_SECRET_OPENAI_API_KEY' > config/openai_api_key
```

```
$ python main.py default
```

### Controlling:

- `p` or `right mouse`: start/stop recording
- `Space` or `left mouse`: pause/unpause recording
- `q`: exit

On stopping the recording, the transcription and post-processing is invoked, but not on pausing the recording.

### Voice Activation (VAD)

To enable VAD, you need to set `enable_vad: true` in your profile.

This adds the control:

- `v`: start/stop recording with voice activation

VAD is sketchy, though.

You can still use normal recording with VAD enabled. You can disable it as it slows down application startup.

### Profiles

Profiles consist of:

- `context` for transcribing and post-processing, see next section
- `enable_vad` whether or not to enable VAD, a bool
- `output` directory, a string

Output will be written to a timestamped file in the output directory.

If you specify `--output filename` on the command line, the specified filename will be used, ignoring the output directory.

### Contexts

Contexts consist of:

- `instructions` for the post-processor, either a filename to load from or a list of strings
- `topic` for the post-processor to give some context, a list of strings
- `gpt_model` to use for post-processing, either a filename to load from or an object
- `options` to use for post-processing, either a filename to load from or an object
- `tools` to use for the post-processor, either a filename to load from or an object
- `language` to use for the transcriber, a string

Usually, you would want to set the topic, language and choose a model. If you are feeling particularly lucky, you could try to tweak the instructions or even the tools.
