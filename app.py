from flask import Flask, request, send_file, render_template_string
import os
import UnityPy

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Isha Converter iOS - Web</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white flex items-center justify-center h-screen">
    <div class="bg-gray-800 p-8 rounded-2xl shadow-xl w-96">
        <h1 class="text-2xl font-bold mb-2">Isha Converter iOS</h1>
        <p class="text-gray-400 text-sm mb-6">Android → iOS Unity bundle converter</p>
        
        <form action="/convert" method="POST" enctype="multipart/form-data" class="space-y-4">
            <div>
                <label class="block text-sm font-medium mb-2">Select .unity3d File</label>
                <input type="file" name="file" required class="w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700">
            </div>
            <button type="submit" class="w-full py-3 bg-blue-600 hover:bg-blue-700 font-bold rounded-xl transition">CONVERT TO iOS</button>
        </form>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
        
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)
    
    try:
        env = UnityPy.load(input_path)
        for obj in env.objects:
            if obj.type.name == "AssetBundle":
                data = obj.read()
                if hasattr(data, "m_TargetPlatform"):
                    data.m_TargetPlatform = 9
                    obj.save_typetree(data)
                    
        output_filename = "ios_" + file.filename
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        with open(output_path, "wb") as f:
            f.write(env.file.save())
            
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"Conversion failed: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
