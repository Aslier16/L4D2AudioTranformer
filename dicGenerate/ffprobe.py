import ffmpeg

info = ffmpeg.probe("E:\\PythonProject\\L4D2AudioTranformer_All\\output\\sound\\music\\flu\\jukebox\\badman.wav")
info2 = ffmpeg.probe("D:\\Steam\\steamapps\\common\\Left 4 Dead 2\\left4dead2\\sound\\music\\flu\\jukebox\\badman.wav")
print(info)
print(info2)