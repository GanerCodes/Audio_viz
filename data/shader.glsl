#ifdef GL_ES
precision mediump float;
precision mediump int;
#endif

#define PI 3.141592653

varying vec4 vertTexCoord;

// uniform float time;
uniform vec2 res;
uniform vec2 b_a;
uniform vec2 b_d;
uniform float a;
uniform float z;

vec3 rgb2hsv(vec3 c) {vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));float d = q.x - min(q.w, q.y);float e = 1.0e-10;return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);}
vec3 hsv2rgb(vec3 c) {vec4 K = vec4(1.0, 0.66666, 0.33333, 3.0);vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);return c.z * mix(K.xxx, p - K.xxx, c.y);}

/* float f_a(float x, float y) { return (cos(3.0 * x) + sin(3.0 * y)) * (cos(x)*sin(y)+sin(y)*cos(x)); }
float f_v(float x, float y) { return sin(f_a(x, y)+cos(f_a(x, y))); }
float f_1(float x, float y) { return f_v(x, y - 0.5 * 3.141592653); }
float f_2(float x, float y) { return f_v(y - sin(x + y), x - cos(x - y)); }
float d_1(float x, float y) { return f_1(x, y)*f_2(x, y) - 0.3; }
float d_2(float x, float y) { return f_1(x, y) - (0.5 * cos(x) - sin(y)); }
float d_3(float x, float y) { return f_1(x, y) - f_1(x - y, y + x); }
float d_4(float x, float y) { return f_1(x, y) + f_1(cos(x), sin(y)) + f_1(sin(x), cos(y)) - 2.0; }  */

float f(vec2 p) {
    // return pow(mod(abs(p.x) - abs(p.y), 1.0) - 0.5, 2.0) - 0.01;
    return mod(max(abs(p.x), abs(p.y)) - 0.5, 1.0 / ((2.0 + z) / 3.0)) - 0.1;
}
float g(vec2 p, vec2 b) {
    vec2 vs = vec2(
        cos(b.x)*p.y - sin(b.x)*p.x,
        cos(b.y)*p.y - sin(b.y)*p.x);
    // return max(-vs.x, vs.y);
    return vs.x * vs.y;
}

void main() {
    vec2 p = 9.0 * z * (vertTexCoord.xy - vec2(0.5)) * (res / res.y);
    
    float c = 0.0;
    
    float ff = 5.0;
    float l = pow(pow(abs(p.x), ff) + pow(abs(p.y), ff), 1.0 / ff);
    if(g(p, b_a) <= 0 && l >= b_d.x && l <= b_d.y) {
        float q = 0.03 - f(p);
        c = q <= 0.0 ? 0.0 : (
            max(
                0.0,
                0.9 * pow(
                    5.0 * q,
                    2.25)));
    }
    if(c < 0) c = 0.0;
    
    gl_FragColor = vec4(vec3(c), a);
}