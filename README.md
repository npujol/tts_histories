**tts_stories**
===============

The TTS CLI tool allows users to convert text to speech using different APIs and services. 
It provides several options for customizing the output, such as saving the text or sending 
it to Telegram.

## Commands
### `send`
-------------------------------------------------------------------------------------------
Send a file to Telegram.

* Options:
	+ `--path`: The path of the file to send.

### `run_tts`
Run the TTS conversion process using the specified options:
+ Options:
	+ `--source`: The source text or URL to convert.
	+ `--out_path`: The output directory for the converted audio files.
	+ `--google/--no-google`: Enable or disable Google API usage (default: False).
	+ `--save_text/--no_save_text`: Enable or disable saving the text output (default: False).
	+ `--telegram/--no-send`: Enable or disable sending the output to Telegram (default: False).
```bash
$ python cli.py send
```

#### Options
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
$ python cli.py run-tts
```


## Environment variables
The environment variable path is the following: [here](./.env)

```
TELEGRAM_CHANNEL_ID=-1000000000000
```

|Name|Description|
|---|---|
|`TELEGRAM_CHANNEL_ID`|The ID of the Telegram channel to send the audio files to.|

## Setup Telegram handler
[How to set up the Telegram handler?](https://github.com/Nekmo/telegram-upload)

Credentials should be saved in ~/.config/telegram-upload.json and ~/.config/telegram-upload.session.