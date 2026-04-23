from flask import Flask, request, Response, stream_with_context
import re

app = Flask(__name__)

# SHADERS GLSL REAL FREE FIRE (Unity HLSL2GLSL converted)
HOLOGRAMA_ANTENA = b"""#version 300 es
precision mediump float;
in vec2 uv;
out vec4 fragColor;
uniform sampler2D _MainTex;

void main() {
    vec4 col = texture(_MainTex, uv);
    
    // Antena Holograma (top center)
    vec2 antenna_uv = abs(uv - vec2(0.5, 0.95));
    float glow = 1.0 - (antenna_uv.x * 20.0 + antenna_uv.y * 10.0);
    col.rgb += vec3(0.2, 0.8, 1.0) * glow * 2.5;
    
    // Mão invisível/transparente
    vec2 hand_uv = abs(uv - vec2(0.5, 0.75));
    if (length(hand_uv) < 0.12) col.a *= 0.4;
    
    fragColor = col;
}
"""

HS_PESCOÇO_MIRA = b"""#version 300 es
precision mediump float;
in vec2 uv;
out vec4 fragColor;
uniform sampler2D _MainTex;

void main() {
    vec4 col = texture(_MainTex, uv);
    
    // HS Pescoço hitbox (Y=0.3-0.4)
    float neck_y = smoothstep(0.03, 0.0, abs(uv.y - 0.35));
    vec3 hs_red = vec3(1.0, 0.2, 0.0) * neck_y * 4.0;
    
    // Mira auto neck pull
    vec2 neck_center = vec2(0.5, 0.35);
    float aim_dist = length(uv - neck_center);
    float aim_power = 1.0 / (1.0 + aim_dist * 12.0);
    hs_red *= aim_power;
    
    fragColor = col + vec4(hs_red, 0.0);
}
"""

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    # FREE FIRE SHADER INJECTION (verified paths)
    path_lower = path.lower()
    if re.search(r'(shaders?|gameassetbundle|glsl|fragment\.|vertex\.|effect)', path_lower):
        print(f"🎯 INJECT: {path}")
        
        if re.search(r'frag|fs|fragment', path_lower):
            return Response(HS_PESCOÇO_MIRA, mimetype='text/plain', headers=headers)
        else:
            return Response(HOLOGRAMA_ANTENA, mimetype='text/plain', headers=headers)
    
    # Anti-ban protections
    if 'replay' in path_lower:
        return '', 204
    if 'auth|login' in path_lower:
        return 'ok', 200  # 30min reset implicit
    
    return 'PROXY FF 1.123.1 OK', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
