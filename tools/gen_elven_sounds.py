"""Author deterministic nonverbal breath/formant whispers as Minecraft mono Vorbis."""
import io,json,shutil,subprocess,wave
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'first_party_mods/alfheim_companion/src/main/resources/assets/alfheim_companion'

def voice(seed):
    rng=np.random.default_rng(seed);rate=24000;duration=2.1+(seed%3)*.28
    t=np.arange(int(rate*duration))/rate;noise=rng.normal(0,1,len(t))
    spectrum=np.fft.rfft(noise);freq=np.fft.rfftfreq(len(t),1/rate)
    # Airy consonants under moving, soft vowel resonances; no intelligible words.
    air=np.fft.irfft(spectrum*((freq>850)&(freq<6500)),n=len(t))
    phrase=np.zeros_like(t);pitch=108+(seed%6)*19
    phase=2*np.pi*np.cumsum(pitch*(1+.035*np.sin(t*6)))/rate
    for i,center in enumerate(np.linspace(.3,duration-.3,4+seed%2)):
        env=np.exp(-((t-center)/(.09+.045*(i%3)))**2)
        f1=(360,520,420,650)[(seed+i)%4];f2=(1200,1750,2050)[(seed+i)%3]
        bands=np.exp(-.5*((freq-f1)/140)**2)+.5*np.exp(-.5*((freq-f2)/260)**2)
        breath=np.fft.irfft(spectrum*bands,n=len(t))
        hum=sum(np.sin(phase*h)*np.exp(-((pitch*h-f1)/240)**2)/h for h in range(1,24))
        phrase+=env*(breath*.8+hum*.13+air*.06)
    fade=np.minimum(1,t/.15)*np.minimum(1,(duration-t)/.2)
    phrase*=fade;phrase=phrase/(max(abs(phrase))+.00001)*.65
    return rate,(phrase*32767).astype('<i2')

def main():
    ffmpeg=shutil.which('ffmpeg');assert ffmpeg,'Vorbis encoder required'
    folder=ASSETS/'sounds/elf';folder.mkdir(parents=True,exist_ok=True)
    for i in range(6):
        rate,samples=voice(1700+i);wav=io.BytesIO()
        with wave.open(wav,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(samples.tobytes())
        subprocess.run([ffmpeg,'-v','error','-y','-i','pipe:0','-c:a','libvorbis','-q:a','5',str(folder/f'murmur_{i}.ogg')],input=wav.getvalue(),check=True)
    path=ASSETS/'sounds.json';sounds=json.loads(path.read_text())
    sounds['elf.murmur']={'subtitle':'subtitles.alfheim_companion.elf.murmur','sounds':[{'name':f'alfheim_companion:elf/murmur_{i}','volume':.28,'pitch':.94+i*.025,'attenuation_distance':8} for i in range(6)]}
    path.write_text(json.dumps(sounds,indent=2)+'\n')
    path=ASSETS/'lang/en_us.json';lang=json.loads(path.read_text());lang['subtitles.alfheim_companion.elf.murmur']='Elf whispers';path.write_text(json.dumps(lang,indent=2)+'\n')
    print('Authored six mono Vorbis elven murmurs; quiet local ambience with subtitles')

if __name__=='__main__':main()
