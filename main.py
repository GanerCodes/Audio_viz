import subprocess, itertools, time, json
import numpy as np

song_name = "/mnt/laptop_srv/personal/Auto-Youtube-Playlist-Archiver/Music/\
Different Heaven - Pentakill (ft. ReesaLunn) [Official Video]_Rpr_HNJ0Y3A.mp3"

song_data_file = "./song.raw"
sample_rate    = 48000
channel_count  = 1
generate_pcm   = True

if generate_pcm:
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", song_name, "-ac", str(channel_count), "-ar", str(sample_rate),
        "-f", "s16le", "-acodec", "pcm_s16le", song_data_file])

song_data = np.array(np.memmap(song_data_file, dtype='h', mode='r'))

def window(data, func=np.average,
           para:int|tuple[int,int]=(1,1),
           step=1, clip=False):
    b, f = (para // 2, para // 2) if isinstance(para, int) else para
    s, e = (b, len(data) - f) if clip else (0, len(data))
    return (func(data[i-b : i+f]) for i in range(s, e, step))

def aprage(data, degree=1):
    v = np.divide(data, np.average(data))
    return v if degree == 1 else np.power(v, degree)

def c(l, x):
    return min(max(0, x), len(l))

SPS = 120
sampc = SPS * (len(song_data) / sample_rate)
slo = SPS // 4
sdc = 8
prop = 0.85

a, f = (aprage(q, 1.5) for q in zip(
    *window(
        song_data,
        func=lambda x: (
            np.average(np.abs(x)),
            np.abs(np.average(np.fft.fft(x)))),
        para=int(sampc),
        step=int(len(song_data) / sampc),
        clip=True)))

l = aprage(
    list(window(
        list(zip(a, f)),
        lambda x: np.average(
            np.abs(
                np.fft.fft(
                    [0.5*v[0]+v[1] for v in x]))),
        para=(slo, 0),
        clip=True)),
    1.85)

s = aprage(
    list(window(
        l,
        func=np.std,
        para=(
            int(prop * sdc),
            int((1 - prop) * sdc)),
        clip=True)),
    1.5)

vals = dict(zip('afls', (a, f, l, s)))
i = {k: (lambda x: (
    tuple(x),
    tuple(itertools.accumulate(x, lambda a, b: a + b))
))(aprage(v)) for k, v in vals.items()}

json.dump({
        'i': i,
        'SPS': SPS,
        'song_name': song_name,
        'sample_rate': sample_rate
    }, open('data.json', 'w'))

exit()
proc = subprocess.Popen(["play", "-t", "raw", "-r", "48k",
        "-e", "signed", "-v", "0.05", "-b", "16", "-c", "1", song_data_file], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

import atexit
atexit.register(lambda: proc.kill())
time.sleep(0.1)

start_time = time.time()
while True:
    time.sleep(1 / 120)
    dt = time.time() - start_time
    t = int(SPS * dt)

    print(f"{dt:<010.5f} | \
{'#'*int(a[t]*3):<11} | \
{'#'*int(f[t]*1):<12} | \
{'#'*int(l[t]*2):<14} | \
{'#'*int(s[t]*5):<15}")
