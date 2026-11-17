import json, math, os, subprocess, tempfile, wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).parent
story=json.loads((ROOT/'stories/story.json').read_text(encoding='utf-8'))
out=ROOT/'output';out.mkdir(exist_ok=True)
W,H=1280,720
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font=ImageFont.truetype(fontpath,34)

def run(*args): subprocess.run(args,check=True)
def speak(text,path):
    # Edge neural voice when network service is reachable; offline fallback always works.
    try:
        run('edge-tts','--voice','en-US-AriaNeural','--text',text,'--write-media',str(path))
        return path
    except Exception as e:
        print('Neural voice unavailable, using offline fallback:',e)
        wav=path.with_suffix('.wav')
        run('espeak-ng','-v','en-us','-s','145','-w',str(wav),text)
        return wav

def duration(path):
    v=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)])
    return float(v)

def scene_frame(place,caption,t,idx):
    colors={'village':('#8c9dd9','#e6b66a'),'forest':('#4b9c83','#d4e3b2'),'castle':('#9c82c5','#f4d9b1')}
    bg,ground=colors.get(place,colors['village'])
    im=Image.new('RGB',(W,H),bg); d=ImageDraw.Draw(im)
    d.ellipse((1000,65,1110,175),fill='#fff0b1')
    d.rectangle((0,510,W,H),fill=ground)
    if place=='village':
        for x in [80,420,920]:
            d.rectangle((x,300,x+220,520),fill='#ffe5bd',outline='#66536c',width=5)
            d.polygon([(x-25,305),(x+110,205),(x+245,305)],fill='#bb6d78')
            d.rectangle((x+80,405,x+140,520),fill='#8e6576')
    elif place=='forest':
        for x in [75,350,800,1080]:
            d.rectangle((x+55,290,x+95,535),fill='#76533c')
            d.ellipse((x-35,170,x+185,380),fill='#2e735a')
    else:
        d.rectangle((760,235,1100,520),fill='#f5d9dd',outline='#735b85',width=7)
        for x in [740,900,1060]:d.rectangle((x,170,x+70,320),fill='#f5d9dd',outline='#735b85',width=5)
        d.polygon([(740,170),(775,105),(810,170)],fill='#c76e9c')
    # Moving cartoon fox with ears, tail, arms, legs and blinking eyes
    x=330+int(35*math.sin(t*1.2));y=390+int(7*math.sin(t*3))
    d.ellipse((x-110,y+65,x+20,y+115),fill='#db763d',outline='#5d3a31',width=4)
    d.ellipse((x-52,y+5,x+52,y+145),fill='#f59c53',outline='#5d3a31',width=5)
    d.line((x-25,y+132,x-40+int(15*math.sin(t*3)),y+185),fill='#493c4a',width=13)
    d.line((x+25,y+132,x+42-int(15*math.sin(t*3)),y+185),fill='#493c4a',width=13)
    d.line((x-42,y+45,x-75,y+80+int(10*math.sin(t*2))),fill='#f59c53',width=15)
    d.line((x+42,y+45,x+80,y+67-int(10*math.sin(t*2))),fill='#f59c53',width=15)
    d.polygon([(x-50,y-48),(x-35,y-115),(x-4,y-60)],fill='#f59c53',outline='#5d3a31')
    d.polygon([(x+50,y-48),(x+35,y-115),(x+4,y-60)],fill='#f59c53',outline='#5d3a31')
    d.ellipse((x-64,y-80,x+64,y+36),fill='#f59c53',outline='#5d3a31',width=5)
    d.ellipse((x-40,y-2,x+40,y+36),fill='#ffe5c3')
    if t%4<3.8:
        for ex in [-25,25]:d.ellipse((x+ex-5,y-34,x+ex+5,y-20),fill='#282c3b')
    else:
        for ex in [-25,25]:d.line((x+ex-5,y-26,x+ex+5,y-26),fill='#282c3b',width=3)
    d.ellipse((x-6,y+4,x+6,y+13),fill='#282c3b')
    # second character rabbit in later scenes
    if idx>0:
        rx=660+int(25*math.sin(t*1.4))
        d.ellipse((rx-45,415,rx+45,550),fill='#ece5f2',outline='#66586c',width=4)
        d.ellipse((rx-35,305,rx-10,440),fill='#ece5f2',outline='#66586c',width=3)
        d.ellipse((rx+10,305,rx+35,440),fill='#ece5f2',outline='#66586c',width=3)
        d.ellipse((rx-48,368,rx+48,470),fill='#ece5f2',outline='#66586c',width=4)
        for ex in [-20,20]:d.ellipse((rx+ex-4,410,rx+ex+4,420),fill='#282c3b')
    # subtitle box
    d.rounded_rectangle((85,615,1195,685),radius=18,fill='#25243b')
    box=d.textbbox((0,0),caption,font=font);tw=box[2]-box[0]
    d.text(((W-tw)/2,631),caption,font=font,fill='white')
    return im

clips=[]
with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    for i,scene in enumerate(story['scenes']):
        audio=speak(scene['narration'],td/f'voice{i}.mp3')
        sec=duration(audio)+0.5
        fps=12
        frames=td/f'frames{i}';frames.mkdir()
        for n in range(math.ceil(sec*fps)):
            scene_frame(scene['place'],scene['caption'],n/fps,i).save(frames/f'{n:05d}.jpg',quality=86)
        clip=td/f'clip{i}.mp4'
        run('ffmpeg','-y','-loglevel','error','-framerate',str(fps),'-i',str(frames/'%05d.jpg'),'-i',str(audio),'-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-shortest',str(clip))
        clips.append(clip)
    concat=td/'concat.txt';concat.write_text(''.join("file '"+str(p)+"'\n" for p in clips))
    run('ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(out/'cartoon.mp4'))
(out/'youtube_metadata.json').write_text(json.dumps({'title':story['title'],'description':story['description'],'made_for_kids':True},indent=2))
print('CREATED',out/'cartoon.mp4')
