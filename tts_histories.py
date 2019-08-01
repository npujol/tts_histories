class Story:
    def __init__(self, filename, language="es"):
        self.filename = filename
        self.language = language
        self.text_story = ""
        self.clean_text()

    def clean_text(self):
        with open(self.filename) as f:
            content = f.readlines()
        content = " ".join([x.strip() for x in content])
        print(content)
        self.text_story = content

    def create_TTS(self):
        from gtts import gTTS

        tts = gTTS(self.text_story, lang=self.language)
        tts.save("{}.mp3".format(self.filename))
        print("Compleat")
