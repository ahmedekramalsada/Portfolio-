import requests, json, base64, os, re

USERNAME = "ahmedekramalsada"
IMAGE_DIR = "images/projects" 
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not os.path.exists(IMAGE_DIR): 
    os.makedirs(IMAGE_DIR, exist_ok=True)

def extract_section(content, section_name):
    pattern = rf"## {section_name}\s*\n(.*?)(?=\n##|$)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""

def main():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.mercy-preview+json" # ضروري لجلب الـ Topics
    } if GITHUB_TOKEN else {}
    
    repos_url = f"https://api.github.com/users/{USERNAME}/repos?sort=updated&per_page=100"
    repos = requests.get(repos_url, headers=headers).json()
    
    project_list = []
    
    for repo in repos:
        # الشرط الجديد: ابحث عن كلمة 'portfolio' في الـ topics الخاصة بالمستودع
        topics = repo.get('topics', [])
        if 'portfolio' not in topics:
            continue
            
        repo_name = repo['name']
        print(f"Adding project: {repo_name}...")

        # (بقية الكود الخاص بجلب الصور والـ README كما هو)
        raw_img_url = f"https://raw.githubusercontent.com/{USERNAME}/{repo_name}/main/preview.webp"
        img_res = requests.get(raw_img_url)
        img_path = ""
        if img_res.status_code == 200:
            img_path = f"{IMAGE_DIR}/{repo_name}.webp"
            with open(img_path, "wb") as f: f.write(img_res.content)
        
        readme_res = requests.get(f"https://api.github.com/repos/{USERNAME}/{repo_name}/readme", headers=headers)
        tech, points = "Various", ["Developed on GitHub."]
        
        if readme_res.status_code == 200:
            decoded = base64.b64decode(readme_res.json()['content']).decode('utf-8')
            tech = extract_section(decoded, "Tech Stack").replace('\n', ', ') or tech
            points = re.findall(r"^[*-]\s*(.*)", extract_section(decoded, "Description"), re.MULTILINE)[:3] or points

        project_list.append({
            "title": repo_name.replace('-', ' ').title(),
            "tech": tech,
            "image": img_path,
            "link": repo['html_url'],
            "points": points
        })
    
    with open("projects.json", "w", encoding="utf-8") as f: 
        json.dump({"projects": project_list}, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
