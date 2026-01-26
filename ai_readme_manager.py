import requests, os, base64, time

# الإعدادات
USERNAME = "ahmedekramalsada"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("MY_GLOBAL_TOKEN")

headers = {"Authorization": f"token {GITHUB_TOKEN}"}

def get_important_content(repo_name):
    """البحث عن ملفات الإعدادات وقراءة محتواها لفهم المشروع"""
    config_files = ['package.json', 'requirements.txt', 'main.py', 'App.js', 'index.html', 'go.mod']
    context = ""
    
    # جلب قائمة الملفات أولاً
    files_res = requests.get(f"https://api.github.com/repos/{USERNAME}/{repo_name}/contents", headers=headers)
    if files_res.status_code != 200: return "No files found."
    
    repo_files = [f['name'] for f in files_res.json()]
    context += f"Files in repo: {', '.join(repo_files)}\n"

    for file in config_files:
        if file in repo_files:
            content_res = requests.get(f"https://api.github.com/repos/{USERNAME}/{repo_name}/contents/{file}", headers=headers)
            if content_res.status_code == 200:
                raw_content = base64.b64decode(content_res.json()['content']).decode('utf-8', errors='ignore')
                context += f"\n--- Content of {file} (first 500 chars) ---\n{raw_content[:500]}\n"
    return context

def generate_readme_ai(repo_name, context):
    """إرسال البيانات لـ Gemini لإنشاء README احترافي"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    Analyze the following files and structure of a GitHub repository named '{repo_name}':
    {context}
    
    Based on this, write a professional README.md. 
    YOU MUST INCLUDE THESE SECTIONS EXACTLY:
    ## Description
    * [3 bullet points describing what the project does based on the code/files provided]
    
    ## Tech Stack
    [List the main technologies, frameworks, and languages found in the files]

    Keep it professional, technical, and concise. Use Markdown.
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    return None

def update_readme(repo_name, new_content):
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/contents/README.md"
    # فحص إذا كان الملف موجوداً لجلب الـ SHA
    current = requests.get(url, headers=headers)
    sha = current.json().get('sha') if current.status_code == 200 else None
    
    data = {
        "message": "AI Generated README (Smart Scan)",
        "content": base64.b64encode(new_content.encode('utf-8')).decode('utf-8'),
    }
    if sha: data["sha"] = sha
    
    res = requests.put(url, json=data, headers=headers)
    return res.status_code in [200, 201]

def main():
    repos = requests.get(f"https://api.github.com/users/{USERNAME}/repos?sort=updated", headers=headers).json()
    
    for repo in repos:
        name = repo['name']
        if repo['fork'] or name == "Portfolio": continue
        
        print(f"🤖 Analyzing {name}...")
        context = get_important_content(name)
        new_readme = generate_readme_ai(name, context)
        
        if new_readme and update_readme(name, new_readme):
            print(f"✅ Successfully updated README for {name}")
        else:
            print(f"❌ Failed to update {name}")
        
        time.sleep(2) # تجنب تجاوز حدود الـ API

if __name__ == "__main__":
    main()
