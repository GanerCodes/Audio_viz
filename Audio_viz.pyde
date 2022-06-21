add_library('minim')
from minim import *
import json, time

def setup():
    global shader, buffer, minim, music
    global song_name, song_data, sample_rate, data_per_second, music_start_time
    fullScreen(P2D)
    # size(1280, 720, P2D)
    frameRate(240)
    
    strokeJoin(ROUND)
    
    shader = loadShader("shader.glsl")
    buffer = createGraphics(width, height, P2D)
    buffer.beginDraw()
    buffer.endDraw()
    
    song_data = json.load(open('./data.json', 'r'))
    song_name = song_data['song_name']
    sample_rate = song_data['sample_rate']
    data_per_second = song_data['SPS']
    
    minim = Minim(this)
    music = minim.loadFile(song_name)
    music.loop()
    music.setGain(-20.0)
    music_start_time = time.time() - 0.05

def draw():
    global ch
    tdt = time.time() - music_start_time
    t = max(1.0, tdt * data_per_second)
    
    idx = int(t)
    fac = 60.0 / data_per_second
    vals_i,vals_a=(i_a,i_f,i_l,i_s),(a_a,a_f,a_l,a_s)=zip(
        *((lerp(y[idx], y[idx+1], t - idx) * fac for y in song_data['i'][x]) for x in 'afls'))
    
    cool = 0.05 * (0.7 * a_l + 0.3 * a_s)
    ch = oclr = 0.5 * (1.0 + cos(0.4 * cool))
    
    def sc(v=None, alf=1.0):
        global ch
        if v is None:
            v = ch
        ch = v % 1.0
        colorMode(HSB, 1.0)
        stroke(ch, 1.0, 1.0, alf)
    sc()
    
    ang = PI * cos(0.035 * a_a) + 0.42 * cool + 0.03 * a_s
    shader.set("b_a", -(cool + QUARTER_PI) + ang, -cool + ang)
    shader.set("b_d", 1.0 + 4*i_a, 4*i_a + pow(2*i_a, 2.5))
    shader.set("a", i_a)
    shader.set("z", (2.0 + pow(1.1 * i_a, 1.25)) / 3.0)
    shader.set("res", float(width), float(height))
    buffer.filter(shader)
    background(0)
    image(buffer, 0, 0)
    
    pushMatrix()
    translate(width / 2.0, height / 2.0)
    sca_fac = width / 1300.0
    scale(sca_fac)
    translate(-width / 2.0, -height / 2.0)
    
    fa = i_a * 55.0
    fq = 5.0 + 25.0 * ((2.0 + i_l) / 3.0) + 2.0 * (1.0 + cos(0.3 * a_s))
    k1 = fq + fa * (1.0 + cos(0.05 * a_a)) * (1.0 + 0.5 * sin(0.02 * a_s))
    k2 = fq + fa * (1.0 + sin(0.05 * a_a)) * (1.0 + 0.5 * cos(0.02 * a_s))
    
    p1, p2 = (-k1, 0), (k1, 0)
    p3, p4 = (0, -k2), (0, k2)
    
    # tp1 = PVector.lerp(PVector(*p3), PVector(*p4), (0.5 + (0.5 * (1.0 + cos(0.1 * cool)))) / 2.0)
    # tp2 = PVector.lerp(PVector(*p1), PVector(*p2), (0.5 + (0.5 * (1.0 + sin(0.1 * cool)))) / 2.0)
    
    def rect_line(x1, y1, x2, y2, kf=1.0):
        l = 25 * kf
        pushMatrix()
        rectMode(CENTER)
        translate(0.5 * (x1 + x2), 0.5 * (y1 + y2))
        rotate(atan2(y2 - y1, x2 - x1))
        d = dist(x1, y1, x2, y2)
        q = d/2.0-l
        line(-q, l/2.0, q, l/2.0)
        line(-q, -l/2.0, q, -l/2.0)
        arc(q, 0, l, l, -HALF_PI, HALF_PI)
        arc(-q, 0, l, l, HALF_PI, PI+HALF_PI)
        popMatrix() 
    
    def do_lines(n=4, mn=None, kf=1, ic=0):
        if mn is None: mn = n+1
        
        s = 0.675
        
        pushMatrix()
        rotate(ang / mn)
        alf = min(1.0, 1.5 * n)
        scale(alf)
        w = 10.0 * pow(s, mn - n)
        strokeWeight(0.3 * w)
        stroke(oclr, 1.0, 1.0, alf)
        circle(0, 0, 2.0 * kf * max(k1, k2))
        sc(alf=alf)
        strokeWeight(w)
        pushMatrix()
        rect_line(*[kf*o for o in p1 + p2], kf=kf)
        popMatrix()
        
        pushMatrix()
        rect_line(*[kf*o for o in p3 + p4], kf=kf)
        popMatrix()
        
        if n > 0:
            for x, y in ((p1, p2), (p3, p4))[ic%2==0]:
                sc(ch + 0.05 * n / mn)
                pushMatrix()
                translate(x, y)
                do_lines(n - 1, mn, s * kf, ic+1)
                popMatrix()
    
        popMatrix()
    pushMatrix()
    translate(width / 2, height / 2)
    m = pow(1.25 * i_f, 2.05) + pow(i_s, 2.0)
    translate(random(-m, m), random(-m, m))
    sc()
    noFill()
    do_lines(5.0 * i_a, mn=6)
    popMatrix()
    
    popMatrix()
    
    colorMode(RGB, 1.0)
    stroke(1)
    fill(1)
    strokeWeight(5)
    for i, v in enumerate(vals_i):
        y = 20 * i + 10
        line(0, y, 100 * v, y)
    
    
    noStroke()
    textAlign(RIGHT)
    text("{}\n\n{}\n{}\n{}\n{}\n\n{}\n{}\n{}\n{}".format(frameRate, *(vals_i + vals_a)), width, 20)

def keyPressed():
    global shader
    try:
        shader = loadShader("shader.glsl")
    except:
        pass
