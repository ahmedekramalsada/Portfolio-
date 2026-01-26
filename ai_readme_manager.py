import requests, os, base64, time

# الإعدادات - تأكد من صحة اسم المستخدم
USERNAME = "ahmedekramalsada"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("MY_GLOBAL_TOKEN")

headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def check_auth():
    """فحص أولي للتوكن قبل بدء العمل"""
    if not GITHUB_TOKEN:
        print("🛑 ERROR: MY_GLOBAL_TOKEN is empty! Check your GitHub Secrets.")
        return False
    res = requests.get("https://api.github.com/user", headers=headers)
    if res.status_code != 200:
        print(f"🛑 AUTH ERROR: Token invalid. Status: {res.status_code}, Message: {res.json().get('message')}")
        return False
    print(f"✅ Auth successful as: {res.json().get('login')}")
    return True

def get_important_content(repo_name):
    config_files = ['package.json', 'requirements.txt', 'main.py', 'App.js', 'index.html']
    context = ""
    files_res = requests.get(f"https://api.github.com/repos/{USERNAME}/{repo_name}/contents", headers=headers)
    
    if files_res.status_code != 200:
        return f"Error fetching files: {files_res.status_code}"
    
    repo_files = [f['name'] for f in files_res.json()]
    for file in config_files:
        if file in repo_files:
            content_res = requests.get(f"https://api.github.com/repos/{USERNAME}/{repo_name}/contents/{file}", headers=headers)
            if content_res.status_code == 200:
                raw = base64.b64decode(content_res.json()['content']).decode('utf-8', errors='ignore')
                context += f"\nFile {file}:\n{raw[:500]}\n"
    return context

def generate_readme_ai(repo_name, context):
    if not GEMINI_API_KEY:
        print("🛑 ERROR: GEMINI_API_KEY is missing!")
        return None
    
    # تغيير الرابط إلى v1 بدلاً من v1beta وتأكيد اسم الموديل
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"Write a professional README.md for the GitHub repository '{repo_name}'. Include exactly these sections: ## Description (3 bullet points) and ## Tech Stack. Context: {context}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        res = requests.post(url, json=payload, timeout=30)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            # إذا فشل v1، سنحاول تجربة gemini-pro كخيار احتياطي
            print(f"⚠️ v1 failed, trying fallback model...")
            fallback_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
            res = requests.post(fallback_url, json=payload, timeout=30)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text']
            
            print(f"🛑 Gemini AI Error: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"🛑 AI Request failed: {e}")
    return None

def update_readme(repo_name, new_content):
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/contents/README.md"
    
    # جلب الـ SHA إذا كان الملف موجوداً
    current = requests.get(url, headers=headers)
    sha = current.json().get('sha') if current.status_code == 200 else None
    
    payload = {
        "message": "AI Generated README",
        "content": base64.b64encode(new_content.encode('utf-8')).decode('utf-8'),
    }
    if sha: payload["sha"] = sha
    
    res = requests.put(url, json=payload, headers=headers)
    
    if res.status_code in [200, 201]:
        return True
    else:
        print(f"❌ Failed Update for {repo_name}: {res.status_code} - {res.json().get('message')}")
        print(f"   Details: {res.json()}") # هذا سيطبع السبب الدقيق مثل 'permissions' أو 'not found'
        return False

def main():
    if not check_auth(): return
    
    repos = requests.get(f"https://api.github.com/users/{USERNAME}/repos?sort=updated", headers=headers).json()
    
    for repo in repos:
        name = repo['name']
        if repo['fork'] or name == "Portfolio": continue
        
        print(f"🤖 Processing {name}...")
        context = get_important_content(name)
        new_content = generate_readme_ai(name, context)
        
        if new_content:
            if update_readme(name, new_content):
                print(f"✅ Done: {name}")
            else:
                print(f"❌ Failed: {name}")
        time.sleep(1)

if __name__ == "__main__":
    main()
