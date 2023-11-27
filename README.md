# DrDictaphone

Dictation app for the terminal, using Whisper for transcription and ChatGPT for post-processing.

### Running

```
$ cat .env
API_KEY=YOUR_SECRET_OPENAI_API_KEY
LOG_LEVEL=INFO
LOG_FILE=drdictaphone.log
```

```
$ python main.py --context context/transcribe-en.yaml --output output.txt
```

### Controlling:

- `p` or `right mouse`: start/stop recording
- `Space` or `left mouse`: pause/unpause recording
- `q`: exit

On stopping the recording, the transcription and post-processing is invoked, but not on pausing the recording.

### Voice Activation (VAD)

You can start with `--enable-vad`.

```
$ python main.py --context context/transcribe-de.yaml --output output.txt --enable-vad
```

This adds the control:

- `v`: start/stop recording with voice activation

VAD is sketchy, though.

### Contexts

Contexts consist of

- `instructions` for the post-processor, either a filename to load from or a list of strings
- `topic` for the post-processor to give some context, a list of strings
- `gpt_model` to use for post-processing, either a filename to load from or an object
- `options` to use for post-processing, either a filename to load from or an object
- `tools` to use for the post-processor, either a filename to load from or an object
- `language` to use for the transcriber, a string

Usually, you would want to set the topic, language and choose a model. If you are feeling particularly lucky, you could try to tweak the instructions or even the tools.
