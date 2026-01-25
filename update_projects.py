import requests, json, base64, os, re

USERNAME = "ahmedekramalsada"
PORTFOLIO_REPO = "Portfolio"
IMAGE_DIR = "images/projects" 
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# إنشاء مجلد الصور إذا لم يكن موجوداً
if not os.path.exists(IMAGE_DIR): 
    os.makedirs(IMAGE_DIR, exist_ok=True)

def extract_section(content, section_name):
    # تحسين الـ Regex ليكون أكثر مرونة مع المسافات
    pattern = rf"## {section_name}\s*\n(.*?)(?=\n##|$)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""

def main():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    
    # جلب جميع المستودعات العامة
    repos_url = f"https://api.github.com/users/{USERNAME}/repos?sort=updated&per_page=100"
    repos = requests.get(repos_url, headers=headers).json()
    
    project_list = []
    
    for repo in repos:
        # تخطي مستودع الموقع نفسه أو الـ Forks
        if repo['name'].lower() == PORTFOLIO_REPO.lower() or repo['fork']: 
            continue
            
        repo_name = repo['name']
        print(f"Processing: {repo_name}...")

        # 1. محاولة تحميل الصورة (preview.webp)
        raw_img_url = f"https://raw.githubusercontent.com/{USERNAME}/{repo_name}/main/preview.webp"
        img_res = requests.get(raw_img_url)
        img_path = ""
        
        if img_res.status_code == 200:
            img_path = f"{IMAGE_DIR}/{repo_name}.webp"
            with open(img_path, "wb") as f: 
                f.write(img_res.content)
        
        # 2. جلب الـ README واستخراج البيانات
        readme_res = requests.get(f"https://api.github.com/repos/{USERNAME}/{repo_name}/readme", headers=headers)
        tech, points = "Various", ["Developed on GitHub."]
        
        if readme_res.status_code == 200:
            content_b64 = readme_res.json()['content']
            decoded = base64.b64decode(content_b64).decode('utf-8')
            
            # استخراج التقنيات والنقاط الوصفية
            extracted_tech = extract_section(decoded, "Tech Stack")
            if extracted_tech:
                tech = extracted_tech.replace('\n', ', ')
            
            extracted_desc = extract_section(decoded, "Description")
            if extracted_desc:
                # استخراج أول 3 نقاط تبدأ بـ * أو -
                found_points = re.findall(r"^[*-]\s*(.*)", extracted_desc, re.MULTILINE)
                if found_points:
                    points = found_points[:3]

        project_list.append({
            "title": repo_name.replace('-', ' ').title(),
            "tech": tech,
            "image": img_path, # سيكون فارغاً إذا لم توجد صورة
            "link": repo['html_url'],
            "points": points
        })
    
    # حفظ النتيجة النهائية
    with open("projects.json", "w", encoding="utf-8") as f: 
        json.dump({"projects": project_list}, f, indent=4, ensure_ascii=False)
    print("Successfully updated projects.json")

if __name__ == "__main__":
    main()