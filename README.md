# tts_stories

The TTS CLI tool allows users to convert text to speech using different APIs and services.
It provides several options for customizing the output, such as saving the text or sending
it to Telegram.

## Commands

### `send`

---
Send a file to Telegram.

Options:

* `--path`: The path of the file to send.

### `run_tts`

Run the TTS conversion process using the specified options:

#### Options

* `--source`: The source text or URL to convert.
* `--out_path`: The output directory for the converted audio files.
* `--google/--no-google`: Enable or disable Google API usage (default: False).
* `--save_text/--no_save_text`: Enable or disable saving the text output (default: False).
* `--telegram/--no-send`: Enable or disable sending the output to Telegram (default: False).

```bash
python cli.py send
```

##### `--source`

The source text or URL to convert. This option is required and could be either a local path or a URL.
For the URL option, the available loaders are Wattpad and AO3 HTML export.

##### `--out_path`

The output directory for the converted audio files. The default value is the current path.

##### `--google/--no-google`

Enable or disable Google TTS usage (default: False).

##### `--save_text/--no_save_text`

Enable or disable saving the text output (default: False).

##### `--telegram/--no-send`

Enable or disable sending the output to Telegram (default: False).

#### Example

```bash
python cli.py run-tts
```

## Environment variables

The environment variable path is the following: [here](./.env)

```plain
TELEGRAM_CHANNEL_ID=-1000000000000
```

|Name|Description|
|---|---|
|`TELEGRAM_CHANNEL_ID`|The ID of the Telegram channel to send the audio files to.|

## Setup Telegram handler

[How to set up the Telegram handler?](https://github.com/Nekmo/telegram-upload)

Credentials should be saved in ~/.config/telegram-upload.json and ~/.config/telegram-upload.session.

## TTS Processors

Available TTS Processors

* [Coqui TTS](https://github.com/coqui-ai/TTS)
* [Google TTS](https://github.com/pndurette/gTTS)

### Coqui TTS

The models for the languages are available in the `app/tts_processors/coqui.py` file.
When is a language without a defined model, it will use the first available model.

To add or override a defined model, add it in the `app/tts_processors/coqui.py` file.
The structure of the new models should be, the language code as the key and the TTSModelConfig as the value.:

```json
{
	Language.SPANISH: TTSModelConfig(
		model_name="tts_models/es/css10/vits",
		sentence_count=10,
		type=TTSModelType.SINGLE,
		shall_add_speaker=True
	)
}
```

### TTSModelConfig

|Name|Description|
|---|---|
|`model_name`| The name of the model. |
|`sentence_count`| The number of sentences in the model. |
|`type`| The type of the model, It could be `TTSModelType.SINGLE` or `TTSModelType.MULTI`. `MULTI` means that the model can be used for more that one language. |
|`shall_add_speaker`| Whether to add the speaker to the model, this element override the original voice and use the voice of the given speaker. |

**How to add a new speaker?**

The new speaker voice file should be added in the folder [`app/tts_processors/speakers/`](./app/tts_processors/speakers/new_me.wav).

### TODO

* [ ] Include a environment variable to get the language setting from the user config file.
* [ ] Add the `--speaker` option to get the speaker voice from the user config file.
* [ ] Add the `--speaker_wav` option to get the speaker voice from the user config file.
