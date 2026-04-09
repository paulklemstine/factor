// ═══════════════════════════════════════════════════════════════════
// ECSTASIS 4 — PSYCHEDELIC VISUAL ENGINE
// ═══════════════════════════════════════════════════════════════════
// WebGL 2.0 pipeline for audio-reactive psychedelic visuals.
// Implements: fractals, reaction-diffusion, kaleidoscope,
// sacred geometry, tunnels, form constants, feedback loops.
// ═══════════════════════════════════════════════════════════════════

const Visuals = (function() {
"use strict";

// ─── SHADER SOURCES ─────────────────────────────────────────────

const VERTEX_SHADER = `#version 300 es
in vec2 a_position;
out vec2 v_uv;
void main() {
    v_uv = a_position * 0.5 + 0.5;
    gl_Position = vec4(a_position, 0.0, 1.0);
}`;

// Main psychedelic fragment shader — combines multiple visual modes
const PSYCHEDELIC_FRAG = `#version 300 es
precision highp float;

in vec2 v_uv;
out vec4 fragColor;

uniform float u_time;
uniform float u_beat;
uniform float u_kick;
uniform float u_snare;
uniform float u_hihat;
uniform float u_bassFreq;
uniform float u_bassCutoff;
uniform float u_energy;
uniform float u_spectrum[16];
uniform float u_bpm;
uniform float u_mode;        // 0=fractal, 1=tunnel, 2=reaction-diff, 3=sacred, 4=warp
uniform float u_kaleidoscope; // number of symmetry folds
uniform float u_feedback;
uniform vec2 u_resolution;
uniform sampler2D u_prevFrame;
uniform sampler2D u_rdTexture;

#define PI 3.14159265359
#define TAU 6.28318530718

// ─── Utility Functions ───

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

vec2 rotate2d(vec2 p, float a) {
    float s = sin(a), c = cos(a);
    return vec2(p.x*c - p.y*s, p.x*s + p.y*c);
}

// Complex multiplication
vec2 cmul(vec2 a, vec2 b) {
    return vec2(a.x*b.x - a.y*b.y, a.x*b.y + a.y*b.x);
}

// ─── Fractal Functions ───

float mandelbrot(vec2 c, int maxIter) {
    vec2 z = vec2(0.0);
    int i;
    for (i = 0; i < 256; i++) {
        if (i >= maxIter) break;
        z = cmul(z, z) + c;
        if (dot(z, z) > 4.0) break;
    }
    if (i >= maxIter) return 0.0;
    // Smooth coloring
    float sl = float(i) - log2(log2(dot(z,z))) + 4.0;
    return sl / float(maxIter);
}

float julia(vec2 z, vec2 c, int maxIter) {
    int i;
    for (i = 0; i < 256; i++) {
        if (i >= maxIter) break;
        z = cmul(z, z) + c;
        if (dot(z, z) > 4.0) break;
    }
    if (i >= maxIter) return 0.0;
    float sl = float(i) - log2(log2(dot(z,z))) + 4.0;
    return sl / float(maxIter);
}

// ─── Tunnel / Wormhole ───

vec3 tunnel(vec2 uv, float t) {
    vec2 p = uv - 0.5;
    float r = length(p);
    float a = atan(p.y, p.x);
    
    // Infinite tunnel depth
    float depth = 0.5 / (r + 0.001);
    float tex_x = a / TAU + 0.5;
    float tex_y = depth + t * 0.5;
    
    // Tunnel walls pattern
    float pattern = sin(tex_x * 12.0 + t) * cos(tex_y * 8.0 - t * 0.3);
    pattern += sin(tex_x * 6.0 - t * 0.7) * sin(tex_y * 4.0 + t * 0.5);
    pattern = pattern * 0.5 + 0.5;
    
    // Color based on depth and angle
    float hue = fract(tex_y * 0.1 + u_bassFreq * 0.001 + t * 0.05);
    float sat = 0.7 + 0.3 * pattern;
    float val = pattern * (1.0 - smoothstep(0.0, 0.05, r)) * 0.3 + pattern * 0.7;
    val *= 1.0 - smoothstep(3.0, 8.0, depth); // fade at infinity
    
    // Kick pulse — radial expansion
    val += u_kick * 0.3 * (1.0 - smoothstep(0.0, 0.3, r));
    
    return hsv2rgb(vec3(hue, sat, clamp(val, 0.0, 1.0)));
}

// ─── Sacred Geometry ───

float flowerOfLife(vec2 p, float scale) {
    p *= scale;
    float d = 1e10;
    // Central circle plus 6 surrounding
    d = min(d, abs(length(p) - 1.0));
    for (int i = 0; i < 6; i++) {
        float a = float(i) * TAU / 6.0;
        vec2 c = vec2(cos(a), sin(a));
        d = min(d, abs(length(p - c) - 1.0));
    }
    // Second ring
    for (int i = 0; i < 6; i++) {
        float a = float(i) * TAU / 6.0 + TAU / 12.0;
        vec2 c = vec2(cos(a), sin(a)) * 1.732;
        d = min(d, abs(length(p - c) - 1.0));
    }
    return smoothstep(0.06, 0.0, d);
}

float metatronsCube(vec2 p, float scale) {
    p *= scale;
    float d = 1e10;
    
    // 13 circles of Fruit of Life
    d = min(d, abs(length(p) - 1.0));
    for (int i = 0; i < 6; i++) {
        float a = float(i) * TAU / 6.0;
        vec2 c = vec2(cos(a), sin(a)) * 2.0;
        d = min(d, abs(length(p - c) - 1.0));
        // Lines between all pairs (Metatron's Cube)
        for (int j = i + 1; j < 6; j++) {
            float a2 = float(j) * TAU / 6.0;
            vec2 c2 = vec2(cos(a2), sin(a2)) * 2.0;
            // Line distance
            vec2 ab = c2 - c;
            float t2 = clamp(dot(p - c, ab) / dot(ab, ab), 0.0, 1.0);
            d = min(d, length(p - c - ab * t2));
        }
    }
    return smoothstep(0.05, 0.0, d);
}

float sriYantra(vec2 p, float scale) {
    p *= scale;
    float d = 0.0;
    // Concentric triangles — simplified
    for (int i = 0; i < 5; i++) {
        float s = 1.0 + float(i) * 0.5;
        vec2 rp = rotate2d(p, float(i) * 0.1);
        // Upward triangle
        float t1 = max(abs(rp.x) * 0.866 + rp.y * 0.5, -rp.y * 0.5 + 0.3) - s * 0.5;
        // Downward triangle
        float t2 = max(abs(rp.x) * 0.866 - rp.y * 0.5, rp.y * 0.5 - 0.3) - s * 0.5;
        d += smoothstep(0.05, 0.0, abs(t1)) * 0.3;
        d += smoothstep(0.05, 0.0, abs(t2)) * 0.3;
    }
    return clamp(d, 0.0, 1.0);
}

// ─── Reaction-Diffusion (read from texture) ───

vec3 reactionDiffusion(vec2 uv) {
    vec4 rd = texture(u_rdTexture, uv);
    float v = rd.g;
    
    // Color mapping — chemical concentrations to psychedelic colors
    float hue = fract(v * 2.0 + u_time * 0.02 + u_bassFreq * 0.002);
    float sat = 0.6 + 0.4 * v;
    float val = 0.1 + 0.9 * smoothstep(0.0, 0.5, v);
    
    return hsv2rgb(vec3(hue, sat, val));
}

// ─── Warp / Morph ───

vec3 warpField(vec2 uv, float t) {
    vec2 p = (uv - 0.5) * 2.0;
    
    // Domain warping
    float n1 = sin(p.x * 3.0 + t) * cos(p.y * 3.0 - t * 0.7);
    float n2 = cos(p.x * 2.0 - t * 0.5) * sin(p.y * 4.0 + t * 0.3);
    p += vec2(n1, n2) * 0.5 * u_energy;
    
    // Spiral
    float r = length(p);
    float a = atan(p.y, p.x);
    a += r * 2.0 * sin(t * 0.1);
    a += t * 0.3;
    
    float pattern = sin(a * 6.0 + r * 10.0 - t * 2.0);
    pattern += sin(a * 3.0 - r * 5.0 + t);
    pattern = pattern * 0.5 + 0.5;
    
    float hue = fract(a / TAU + r * 0.3 + t * 0.05);
    float sat = 0.7 + 0.3 * pattern;
    float val = pattern * 0.8 + 0.2;
    
    // Audio reactivity
    val += u_kick * 0.2;
    hue += u_snare * 0.1;
    
    return hsv2rgb(vec3(hue, sat, val));
}

// ─── Kaleidoscope Transform ───

vec2 kaleidoscope(vec2 uv, float folds) {
    vec2 p = uv - 0.5;
    float a = atan(p.y, p.x);
    float r = length(p);
    
    // Fold angle
    float segment = TAU / folds;
    a = mod(a, segment);
    if (a > segment * 0.5) a = segment - a;
    
    // Rotate on snare
    a += u_snare * 0.5;
    
    return vec2(cos(a), sin(a)) * r + 0.5;
}

// ─── Form Constants (Klüver) ───

vec3 formConstants(vec2 uv, float t, float type) {
    vec2 p = (uv - 0.5) * 2.0;
    
    // Log-polar transform (retinal → cortical)
    float r = length(p) + 0.001;
    float theta = atan(p.y, p.x);
    vec2 cortical = vec2(log(r), theta);
    
    float pattern = 0.0;
    
    if (type < 1.0) {
        // Type I: Lattice/grating
        pattern = sin(cortical.x * 20.0 + t) * sin(cortical.y * 8.0 - t * 0.5);
    } else if (type < 2.0) {
        // Type II: Cobweb (radial)
        pattern = sin(theta * 12.0 + t) * sin(log(r) * 10.0 - t);
    } else if (type < 3.0) {
        // Type III: Tunnel/funnel
        pattern = sin(log(r) * 15.0 - t * 3.0 + sin(theta * 4.0) * 0.5);
    } else {
        // Type IV: Spiral
        pattern = sin(theta * 6.0 + log(r) * 10.0 - t * 2.0);
    }
    
    pattern = pattern * 0.5 + 0.5;
    
    // Psychedelic coloring
    float hue = fract(pattern * 0.5 + r * 0.3 + t * 0.03 + u_bassFreq * 0.002);
    float sat = 0.6 + 0.4 * pattern;
    float val = pattern;
    
    // Glow at center
    val += 0.3 * exp(-r * 2.0);
    
    return hsv2rgb(vec3(hue, sat, clamp(val, 0.0, 1.0)));
}

// ─── Main ───

void main() {
    vec2 uv = v_uv;
    vec2 aspect = vec2(u_resolution.x / u_resolution.y, 1.0);
    
    // Apply kaleidoscope if enabled
    float folds = u_kaleidoscope;
    if (folds >= 3.0) {
        uv = kaleidoscope(uv, folds);
    }
    
    vec3 color = vec3(0.0);
    float t = u_time;
    
    // Select visual mode
    int mode = int(u_mode);
    
    if (mode == 0) {
        // Fractal — Julia set with audio-reactive parameter
        vec2 z = (uv - 0.5) * 3.0;
        float cr = -0.7 + 0.2 * sin(t * 0.1) + u_energy * 0.1;
        float ci = 0.27015 + 0.1 * cos(t * 0.13) + u_bassCutoff * 0.001;
        float f = julia(z, vec2(cr, ci), 64 + int(u_energy * 64.0));
        float hue = fract(f * 3.0 + t * 0.02 + u_bassFreq * 0.002);
        color = hsv2rgb(vec3(hue, 0.7 + 0.3 * f, f));
    }
    else if (mode == 1) {
        // Tunnel
        color = tunnel(uv, t * (0.5 + u_energy * 0.5));
    }
    else if (mode == 2) {
        // Reaction-Diffusion
        color = reactionDiffusion(uv);
    }
    else if (mode == 3) {
        // Sacred Geometry
        vec2 p = (uv - 0.5) * 2.0 * aspect;
        p = rotate2d(p, t * 0.05 + u_snare * 0.3);
        float scale = 2.0 + sin(t * 0.1) + u_energy;
        float geom = 0.0;
        float sel = mod(t * 0.02, 3.0);
        if (sel < 1.0) geom = flowerOfLife(p, scale);
        else if (sel < 2.0) geom = metatronsCube(p, scale);
        else geom = sriYantra(p, scale);
        
        float hue = fract(t * 0.02 + length(p) * 0.1 + u_bassFreq * 0.002);
        color = hsv2rgb(vec3(hue, 0.6, 0.1)) + geom * hsv2rgb(vec3(hue + 0.5, 0.8, 1.0));
    }
    else if (mode == 4) {
        // Warp field
        color = warpField(uv, t);
    }
    else if (mode == 5) {
        // Form constants
        float formType = mod(t * 0.05, 4.0);
        color = formConstants(uv, t, formType);
    }
    else {
        // Mix / composite
        vec3 c1 = tunnel(uv, t * 0.3);
        float formType = mod(t * 0.03, 4.0);
        vec3 c2 = formConstants(uv, t * 0.7, formType);
        float mix_f = sin(t * 0.05) * 0.5 + 0.5;
        color = mix(c1, c2, mix_f);
    }
    
    // ─── Audio-Reactive Modulations ───
    
    // Kick pulse — brightness flash
    color += vec3(u_kick * 0.15);
    
    // Snare — color shift
    color.r += u_snare * 0.1;
    color.b += u_snare * 0.05;
    
    // Hi-hat — sparkle
    if (u_hihat > 0.3) {
        vec2 sp = fract(uv * 50.0 + t);
        float sparkle = step(0.97, fract(sin(dot(sp, vec2(12.9898, 78.233))) * 43758.5453));
        color += vec3(sparkle * u_hihat * 0.5);
    }
    
    // Spectrum bars in periphery
    float specIdx = floor(uv.x * 16.0);
    float specVal = u_spectrum[int(clamp(specIdx, 0.0, 15.0))];
    if (uv.y < 0.02) {
        color += hsv2rgb(vec3(specIdx / 16.0, 0.8, specVal));
    }
    
    // ─── Feedback Loop ───
    if (u_feedback > 0.0) {
        vec2 fb_uv = uv - 0.5;
        // Rotate and scale previous frame
        fb_uv = rotate2d(fb_uv, 0.01 + u_snare * 0.02);
        fb_uv *= 0.99 + u_kick * 0.01;
        fb_uv += 0.5;
        
        if (fb_uv.x >= 0.0 && fb_uv.x <= 1.0 && fb_uv.y >= 0.0 && fb_uv.y <= 1.0) {
            vec3 prev = texture(u_prevFrame, fb_uv).rgb;
            color = mix(color, prev, u_feedback * 0.85);
        }
    }
    
    // ─── Post-Processing ───
    
    // Bloom (cheap approximation)
    float lum = dot(color, vec3(0.299, 0.587, 0.114));
    if (lum > 0.7) {
        color += (color - 0.7) * 0.5;
    }
    
    // Vignette
    float vig = 1.0 - length((uv - 0.5) * 1.5);
    vig = smoothstep(0.0, 0.7, vig);
    color *= vig;
    
    // Chromatic aberration
    float ca = 0.002 + u_kick * 0.003;
    // Would sample texture at offset for RGB split — simplified here
    color.r *= 1.0 + sin(uv.x * 100.0 + t * 5.0) * ca;
    color.b *= 1.0 + cos(uv.y * 100.0 - t * 3.0) * ca;
    
    // Gamma
    color = pow(clamp(color, 0.0, 1.0), vec3(0.9));
    
    fragColor = vec4(color, 1.0);
}`;

// Reaction-Diffusion compute shader (Gray-Scott model)
const RD_FRAG = `#version 300 es
precision highp float;

in vec2 v_uv;
out vec4 fragColor;

uniform sampler2D u_state;
uniform vec2 u_resolution;
uniform float u_feed;
uniform float u_kill;
uniform float u_dt;

void main() {
    vec2 texel = 1.0 / u_resolution;
    
    // Sample neighborhood (Laplacian)
    vec4 center = texture(u_state, v_uv);
    vec4 left   = texture(u_state, v_uv + vec2(-texel.x, 0.0));
    vec4 right  = texture(u_state, v_uv + vec2( texel.x, 0.0));
    vec4 up     = texture(u_state, v_uv + vec2(0.0,  texel.y));
    vec4 down   = texture(u_state, v_uv + vec2(0.0, -texel.y));
    
    vec2 laplacian = (left.rg + right.rg + up.rg + down.rg - 4.0 * center.rg);
    
    float u = center.r;
    float v = center.g;
    float uvv = u * v * v;
    
    float du = 0.21 * laplacian.r - uvv + u_feed * (1.0 - u);
    float dv = 0.105 * laplacian.g + uvv - (u_feed + u_kill) * v;
    
    float newU = clamp(u + du * u_dt, 0.0, 1.0);
    float newV = clamp(v + dv * u_dt, 0.0, 1.0);
    
    fragColor = vec4(newU, newV, 0.0, 1.0);
}`;

// Simple copy/display shader
const COPY_FRAG = `#version 300 es
precision highp float;
in vec2 v_uv;
out vec4 fragColor;
uniform sampler2D u_texture;
void main() {
    fragColor = texture(u_texture, v_uv);
}`;

// ─── VISUAL ENGINE CLASS ────────────────────────────────────────

class VisualEngine {
    constructor(canvas) {
        this.canvas = canvas;
        this.gl = canvas.getContext('webgl2', {
            alpha: false,
            antialias: false,
            preserveDrawingBuffer: true
        });
        
        if (!this.gl) {
            console.error('WebGL 2 not supported');
            this.fallback = true;
            this.ctx = canvas.getContext('2d');
            return;
        }
        
        this.fallback = false;
        this.gl.getExtension('EXT_color_buffer_float');
        
        // State
        this.time = 0;
        this.mode = 1; // tunnel
        this.kaleidoscope = 6;
        this.feedback = 0.7;
        this.autoMode = true;
        this.modeTime = 0;
        this.modeDuration = 30; // seconds per mode
        
        // Audio data
        this.audioData = {
            beat: 0, kick: 0, snare: 0, hihat: 0,
            bassFreq: 100, bassCutoff: 1000, energy: 0.5,
            spectrum: new Float32Array(16), bpm: 128
        };
        
        this._init();
    }
    
    _init() {
        const gl = this.gl;
        
        // Full-screen quad
        const quadVerts = new Float32Array([-1,-1, 1,-1, -1,1, 1,1]);
        this.quadVAO = gl.createVertexArray();
        gl.bindVertexArray(this.quadVAO);
        const buf = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, buf);
        gl.bufferData(gl.ARRAY_BUFFER, quadVerts, gl.STATIC_DRAW);
        gl.enableVertexAttribArray(0);
        gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
        gl.bindVertexArray(null);
        
        // Compile shaders
        this.mainProgram = this._createProgram(VERTEX_SHADER, PSYCHEDELIC_FRAG);
        this.rdProgram = this._createProgram(VERTEX_SHADER, RD_FRAG);
        this.copyProgram = this._createProgram(VERTEX_SHADER, COPY_FRAG);
        
        // Framebuffers for feedback loop
        this.fbos = [this._createFBO(), this._createFBO()];
        this.currentFBO = 0;
        
        // Reaction-diffusion state textures
        this.rdFBOs = [this._createFBO(512, 512), this._createFBO(512, 512)];
        this.currentRD = 0;
        this._initRD();
        
        // Resize handler
        this._resize();
        window.addEventListener('resize', () => this._resize());
    }
    
    _createShader(type, source) {
        const gl = this.gl;
        const shader = gl.createShader(type);
        gl.shaderSource(shader, source);
        gl.compileShader(shader);
        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
            console.error('Shader compile error:', gl.getShaderInfoLog(shader));
            gl.deleteShader(shader);
            return null;
        }
        return shader;
    }
    
    _createProgram(vertSrc, fragSrc) {
        const gl = this.gl;
        const program = gl.createProgram();
        gl.attachShader(program, this._createShader(gl.VERTEX_SHADER, vertSrc));
        gl.attachShader(program, this._createShader(gl.FRAGMENT_SHADER, fragSrc));
        gl.linkProgram(program);
        if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
            console.error('Program link error:', gl.getProgramInfoLog(program));
            return null;
        }
        return program;
    }
    
    _createFBO(w, h) {
        const gl = this.gl;
        w = w || this.canvas.width || 800;
        h = h || this.canvas.height || 600;
        
        const fbo = gl.createFramebuffer();
        gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
        
        const tex = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, tex);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA16F, w, h, 0, gl.RGBA, gl.FLOAT, null);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        
        gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);
        gl.bindFramebuffer(gl.FRAMEBUFFER, null);
        
        return { fbo, texture: tex, width: w, height: h };
    }
    
    _initRD() {
        const gl = this.gl;
        // Initialize reaction-diffusion with random seeds
        const w = 512, h = 512;
        const data = new Float32Array(w * h * 4);
        for (let i = 0; i < w * h; i++) {
            data[i*4] = 1.0; // u = 1 everywhere
            data[i*4+1] = 0.0; // v = 0 everywhere
            data[i*4+2] = 0.0;
            data[i*4+3] = 1.0;
        }
        // Seed some spots
        for (let s = 0; s < 20; s++) {
            const cx = Math.floor(Math.random() * w);
            const cy = Math.floor(Math.random() * h);
            const r = 3 + Math.floor(Math.random() * 5);
            for (let dy = -r; dy <= r; dy++) {
                for (let dx = -r; dx <= r; dx++) {
                    if (dx*dx + dy*dy <= r*r) {
                        const x = (cx + dx + w) % w;
                        const y = (cy + dy + h) % h;
                        const idx = (y * w + x) * 4;
                        data[idx] = 0.5;
                        data[idx+1] = 0.25;
                    }
                }
            }
        }
        
        for (let i = 0; i < 2; i++) {
            gl.bindTexture(gl.TEXTURE_2D, this.rdFBOs[i].texture);
            gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA16F, w, h, 0, gl.RGBA, gl.FLOAT, data);
        }
    }
    
    _resize() {
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        this.canvas.width = this.canvas.clientWidth * dpr;
        this.canvas.height = this.canvas.clientHeight * dpr;
        
        if (!this.fallback) {
            this.gl.viewport(0, 0, this.canvas.width, this.canvas.height);
            // Recreate feedback FBOs at new size
            this.fbos.forEach(f => {
                this.gl.deleteTexture(f.texture);
                this.gl.deleteFramebuffer(f.fbo);
            });
            this.fbos = [this._createFBO(), this._createFBO()];
        }
    }
    
    updateAudioData(data) {
        Object.assign(this.audioData, data);
    }
    
    setMode(mode) {
        this.mode = mode;
        this.autoMode = false;
    }
    
    setAutoMode(auto) {
        this.autoMode = auto;
    }
    
    setKaleidoscope(folds) {
        this.kaleidoscope = folds;
    }
    
    setFeedback(amount) {
        this.feedback = amount;
    }
    
    render(dt) {
        if (this.fallback) {
            this._renderFallback(dt);
            return;
        }
        
        this.time += dt;
        this.modeTime += dt;
        
        // Auto mode switching
        if (this.autoMode && this.modeTime > this.modeDuration) {
            this.modeTime = 0;
            this.mode = (this.mode + 1) % 7;
        }
        
        const gl = this.gl;
        const ad = this.audioData;
        
        // Step reaction-diffusion (multiple steps per frame for speed)
        if (this.mode === 2) {
            this._stepRD(5);
        }
        
        // ─── Render main visual to FBO ───
        const target = this.fbos[this.currentFBO];
        const source = this.fbos[1 - this.currentFBO];
        
        gl.bindFramebuffer(gl.FRAMEBUFFER, target.fbo);
        gl.viewport(0, 0, target.width, target.height);
        gl.useProgram(this.mainProgram);
        
        // Set uniforms
        const loc = (name) => gl.getUniformLocation(this.mainProgram, name);
        
        gl.uniform1f(loc('u_time'), this.time);
        gl.uniform1f(loc('u_beat'), ad.beat);
        gl.uniform1f(loc('u_kick'), ad.kick);
        gl.uniform1f(loc('u_snare'), ad.snare);
        gl.uniform1f(loc('u_hihat'), ad.hihat);
        gl.uniform1f(loc('u_bassFreq'), ad.bassFreq);
        gl.uniform1f(loc('u_bassCutoff'), ad.bassCutoff);
        gl.uniform1f(loc('u_energy'), ad.energy);
        gl.uniform1f(loc('u_bpm'), ad.bpm);
        gl.uniform1f(loc('u_mode'), this.mode);
        gl.uniform1f(loc('u_kaleidoscope'), this.kaleidoscope);
        gl.uniform1f(loc('u_feedback'), this.feedback);
        gl.uniform2f(loc('u_resolution'), target.width, target.height);
        gl.uniform1fv(loc('u_spectrum[0]'), ad.spectrum);
        
        // Bind previous frame
        gl.activeTexture(gl.TEXTURE0);
        gl.bindTexture(gl.TEXTURE_2D, source.texture);
        gl.uniform1i(loc('u_prevFrame'), 0);
        
        // Bind RD texture
        gl.activeTexture(gl.TEXTURE1);
        gl.bindTexture(gl.TEXTURE_2D, this.rdFBOs[this.currentRD].texture);
        gl.uniform1i(loc('u_rdTexture'), 1);
        
        // Draw
        gl.bindVertexArray(this.quadVAO);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        
        // ─── Copy to screen ───
        gl.bindFramebuffer(gl.FRAMEBUFFER, null);
        gl.viewport(0, 0, this.canvas.width, this.canvas.height);
        gl.useProgram(this.copyProgram);
        gl.activeTexture(gl.TEXTURE0);
        gl.bindTexture(gl.TEXTURE_2D, target.texture);
        gl.uniform1i(gl.getUniformLocation(this.copyProgram, 'u_texture'), 0);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        
        this.currentFBO = 1 - this.currentFBO;
    }
    
    _stepRD(steps) {
        const gl = this.gl;
        gl.useProgram(this.rdProgram);
        
        const loc = (name) => gl.getUniformLocation(this.rdProgram, name);
        
        // Audio-reactive RD parameters
        const feed = 0.037 + this.audioData.energy * 0.02;
        const kill = 0.06 + this.audioData.bassCutoff * 0.00001;
        
        gl.uniform2f(loc('u_resolution'), 512, 512);
        gl.uniform1f(loc('u_feed'), feed);
        gl.uniform1f(loc('u_kill'), kill);
        gl.uniform1f(loc('u_dt'), 1.0);
        
        gl.bindVertexArray(this.quadVAO);
        
        for (let i = 0; i < steps; i++) {
            const target = this.rdFBOs[1 - this.currentRD];
            const source = this.rdFBOs[this.currentRD];
            
            gl.bindFramebuffer(gl.FRAMEBUFFER, target.fbo);
            gl.viewport(0, 0, 512, 512);
            
            gl.activeTexture(gl.TEXTURE0);
            gl.bindTexture(gl.TEXTURE_2D, source.texture);
            gl.uniform1i(loc('u_state'), 0);
            
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
            
            this.currentRD = 1 - this.currentRD;
        }
        
        // Add random seeds occasionally (audio-reactive)
        if (this.audioData.kick > 0.8 && Math.random() < 0.1) {
            this._seedRD();
        }
    }
    
    _seedRD() {
        const gl = this.gl;
        const w = 512, h = 512;
        // Read current state, add seed, write back
        // For performance, we'll just reinit occasionally
        if (Math.random() < 0.01) {
            this._initRD();
        }
    }
    
    _renderFallback(dt) {
        // Canvas 2D fallback for browsers without WebGL2
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;
        this.time += dt;
        
        // Simple psychedelic circles
        ctx.fillStyle = `rgba(0, 0, 0, 0.05)`;
        ctx.fillRect(0, 0, w, h);
        
        const ad = this.audioData;
        const cx = w / 2;
        const cy = h / 2;
        
        for (let i = 0; i < 12; i++) {
            const r = 50 + i * 30 + ad.kick * 50 + Math.sin(this.time + i) * 20;
            const hue = (this.time * 20 + i * 30 + ad.bassFreq * 0.5) % 360;
            ctx.strokeStyle = `hsla(${hue}, 80%, 60%, ${0.5 - i * 0.03})`;
            ctx.lineWidth = 2 + ad.energy * 3;
            ctx.beginPath();
            ctx.arc(cx, cy, r, 0, Math.PI * 2);
            ctx.stroke();
        }
    }
}

return { VisualEngine };

})();
