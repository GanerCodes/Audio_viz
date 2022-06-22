import subprocess, itertools, operator, json, threading
import numpy as np
from scipy import stats
# from numba import jit

song_name = "/home/ganer/Projects/Simulations_Visualizations/Audio_viz/data/song1.mp3"
# song_name = "/home/ganer/Projects/Games/Aebal/aebal/asd/Wax Fang - Majestic.mp3"

song_data_file = "./song.raw"
sample_rate    = 48000
channel_count  = 1
generate_pcm   = True

thread_count = 10
SPS = 120
slo = SPS // 4
sdc = 8
prop = 0.85

if generate_pcm:
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", song_name, "-ac", str(channel_count), "-ar", str(sample_rate),
        "-f", "s16le", "-acodec", "pcm_s16le", song_data_file])
    print("Generated PCM")

song_data = np.array(np.memmap(song_data_file, dtype='h', mode='r'))
sampc = SPS * (len(song_data) / sample_rate)

def window(data, func=np.average,
           para: tuple[int,int]=(1,1),
           step: int=1, clip: bool=False):
    b, f = para
    s, e = (b, len(data) - f) if clip else (0, len(data))
    
    chunks = [range(x-b, x+f) for x in range(s, e, step)]
    arr = np.zeros(len(chunks))
    thread_chunk_count = len(chunks) // thread_count
    print(f"Creating {thread_count} threads for window.")
    
    def thread_func(arr, offset, data, chunks):
        vls = np.zeros(len(chunks))
        vls = [func(data[chunk[0] : chunk[-1]]) for chunk in chunks]
        for i, v in enumerate(vls):
            arr[offset + i] = v
    
    threads = []
    for i in range(0, len(chunks), thread_chunk_count):
        thread = threading.Thread(
            target=thread_func,
            args=(arr, i, data, chunks[i:i+thread_chunk_count]))
        thread.start()
        threads.append(thread)
    
    [t.join() for t in threads]
    
    return arr

def lerp(a, b, c):
    return a + c * (b - a)

def aprage(data, degree=1):
    v = np.divide(data, np.average(data))
    return v if degree == 1 else np.power(v, degree)

def normalize(vals, men=0.5, dev=0.75):
    m, s = np.mean(vals), np.std(vals)
    return [max(0.00001, men + (j if (j := (dev / s * (q - m))) > 0 else -(np.sqrt(abs(j) + 1) - 1))) for q in vals]
    # return np.sqrt(len(vals)) * vals / np.sqrt(np.sum(np.square(vals)))

t_kwargs = {
    'para': (int(sampc), int(sampc)),
    'step': int(len(song_data) / sampc),
    'clip': True}

a = aprage(
    window(
        song_data,
        func=lambda x: np.average(np.abs(x)),
        **t_kwargs), 1.5)
print("Finished first window")
f = aprage(
    window(
        song_data,
        func=lambda x: np.average(np.abs(np.fft.fft(x))),
        **t_kwargs), 1.5)
print("Finished second window")

# a, f = (aprage(q, 1.5) for q in zip(
#     *window(
#         song_data,
#         func=lambda x: (
#             np.average(np.abs(x)),
#             np.abs(np.average(np.fft.fft(x)))),
#         para=(int(sampc), int(sampc)),
#         step=int(len(song_data) / sampc),
#         clip=True)))

l = aprage(
    window(
        np.array([0.5*v1 + v2 for v1, v2 in zip(a, f)]),
        lambda x: np.average(np.abs(np.fft.fft(x))),
        para=(slo, 0),
        clip=True),
    1.85)
print("Finished third window")

s = aprage(
    window(
        l,
        func=np.std,
        para=(
            int(prop * sdc),
            int((1 - prop) * sdc)),
        clip=True),
    1.5)
print("Finished fourth window")

i = {}
for k, v in zip('afls', (a, f, l, s)):
    g = normalize(v)
    i[k] = (tuple(g), tuple(itertools.accumulate(g, operator.add)))
print("Created accumulators")

json.dump({
        'i': i,
        'SPS': SPS,
        'song_name': song_name,
        'sample_rate': sample_rate
    }, open('data.json', 'w'))
print("Wrote JSON - finished!")