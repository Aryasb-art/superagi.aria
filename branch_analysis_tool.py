
#!/usr/bin/env python3
"""
ابزار تحلیل و ادغام خودکار برنچ‌های Integration
"""

import subprocess
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any


class GitBranchAnalyzer:
    """تحلیلگر خودکار برنچ‌های گیت"""
    
    def __init__(self):
        self.main_branch = "main"
        self.integration_branches = [
            "agent-integration-phase2",
            "agent-migration-phase1"
        ]
        self.critical_files = [
            "superagi/agents/aria_agents/",
            "aria_cli.py",
            "aria_mvp_runner.py",
            "main.py",
            "requirements.txt",
            "superagi/controllers/aria_agent.py"
        ]
    
    def run_git_command(self, command: List[str]) -> str:
        """اجرای دستور گیت"""
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"❌ خطا در اجرای دستور: {' '.join(command)}")
            print(f"خطا: {e.stderr}")
            return ""
    
    def get_branch_diff(self, base_branch: str, compare_branch: str) -> Dict[str, Any]:
        """مقایسه دو برنچ"""
        print(f"🔍 مقایسه {base_branch} با {compare_branch}...")
        
        # لیست فایل‌های تغییر یافته
        changed_files = self.run_git_command([
            "git", "diff", "--name-only", 
            f"{base_branch}..origin/{compare_branch}"
        ])
        
        # آمار تغییرات
        stats = self.run_git_command([
            "git", "diff", "--stat", 
            f"{base_branch}..origin/{compare_branch}"
        ])
        
        # کامیت‌های جدید
        commits = self.run_git_command([
            "git", "log", "--oneline", "--no-merges",
            f"{base_branch}..origin/{compare_branch}"
        ])
        
        return {
            "branch": compare_branch,
            "changed_files": changed_files.split('\n') if changed_files else [],
            "stats": stats,
            "commits": commits.split('\n') if commits else [],
            "commit_count": len(commits.split('\n')) if commits else 0
        }
    
    def analyze_file_importance(self, file_path: str) -> Dict[str, Any]:
        """تحلیل اهمیت فایل"""
        importance = "low"
        category = "other"
        
        # فایل‌های حیاتی
        if any(critical in file_path for critical in self.critical_files):
            importance = "critical"
            
        # دسته‌بندی فایل‌ها
        if "aria_agents/" in file_path:
            category = "aria_core"
            importance = "critical"
        elif file_path.endswith(('.py', '.yaml', '.yml')):
            category = "code"
            importance = "high" if importance != "critical" else importance
        elif file_path.endswith(('.md', '.txt', '.pdf')):
            category = "documentation"
            importance = "low"
        elif "test" in file_path.lower():
            category = "tests"
            importance = "medium"
        
        return {
            "file": file_path,
            "importance": importance,
            "category": category
        }
    
    def create_merge_plan(self, analysis_results: List[Dict]) -> Dict[str, Any]:
        """ایجاد طرح merge"""
        merge_plan = {
            "critical_files": [],
            "recommended_files": [],
            "optional_files": [],
            "skip_files": [],
            "conflicts_possible": []
        }
        
        all_changed_files = set()
        
        for result in analysis_results:
            for file_path in result["changed_files"]:
                if file_path:  # اگر فایل خالی نباشد
                    all_changed_files.add(file_path)
        
        # تحلیل هر فایل
        for file_path in all_changed_files:
            file_analysis = self.analyze_file_importance(file_path)
            
            if file_analysis["importance"] == "critical":
                merge_plan["critical_files"].append(file_analysis)
            elif file_analysis["importance"] == "high":
                merge_plan["recommended_files"].append(file_analysis)
            elif file_analysis["importance"] == "medium":
                merge_plan["optional_files"].append(file_analysis)
            else:
                merge_plan["skip_files"].append(file_analysis)
        
        return merge_plan
    
    def check_conflicts(self, branch: str) -> List[str]:
        """بررسی احتمال conflict"""
        try:
            # شبیه‌سازی merge برای بررسی conflict
            self.run_git_command(["git", "checkout", self.main_branch])
            
            # تست merge بدون commit
            result = subprocess.run([
                "git", "merge", "--no-commit", "--no-ff", f"origin/{branch}"
            ], capture_output=True, text=True)
            
            conflicts = []
            if result.returncode != 0:
                # دریافت فایل‌های conflict
                conflict_files = subprocess.run([
                    "git", "diff", "--name-only", "--diff-filter=U"
                ], capture_output=True, text=True)
                
                if conflict_files.stdout:
                    conflicts = conflict_files.stdout.strip().split('\n')
                
                # لغو merge
                subprocess.run(["git", "merge", "--abort"], 
                             capture_output=True, text=True)
            
            return conflicts
            
        except Exception as e:
            print(f"⚠️  خطا در بررسی conflict: {e}")
            return []
    
    def generate_report(self, analysis_results: List[Dict], merge_plan: Dict) -> str:
        """تولید گزارش نهایی"""
        report = f"""
# گزارش تحلیل برنچ‌های Integration
📅 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## خلاصه برنچ‌های بررسی شده:
"""
        
        for result in analysis_results:
            report += f"""
### 🌿 برنچ: {result['branch']}
- 📊 تعداد کامیت‌ها: {result['commit_count']}
- 📁 فایل‌های تغییر یافته: {len(result['changed_files'])}

#### آخرین کامیت‌ها:
```
{chr(10).join(result['commits'][:5])}
```
"""

        report += f"""
## 📋 طرح Merge پیشنهادی:

### 🔴 فایل‌های حیاتی (باید merge شوند):
"""
        for file_info in merge_plan["critical_files"]:
            report += f"- `{file_info['file']}` ({file_info['category']})\n"
        
        report += f"""
### 🟡 فایل‌های توصیه شده:
"""
        for file_info in merge_plan["recommended_files"]:
            report += f"- `{file_info['file']}` ({file_info['category']})\n"
        
        report += f"""
### 🟢 فایل‌های اختیاری:
"""
        for file_info in merge_plan["optional_files"][:10]:  # فقط 10 تا اول
            report += f"- `{file_info['file']}` ({file_info['category']})\n"
        
        if len(merge_plan["optional_files"]) > 10:
            report += f"... و {len(merge_plan['optional_files']) - 10} فایل دیگر\n"
        
        return report
    
    def auto_merge_safe_files(self, merge_plan: Dict) -> bool:
        """merge خودکار فایل‌های امن"""
        print("🚀 شروع merge خودکار فایل‌های امن...")
        
        try:
            # اطمینان از بودن روی main
            self.run_git_command(["git", "checkout", self.main_branch])
            
            # merge فایل‌های حیاتی از برنچ اول
            for branch in self.integration_branches:
                conflicts = self.check_conflicts(branch)
                
                if not conflicts:
                    print(f"✅ merge امن برنچ {branch}")
                    self.run_git_command([
                        "git", "merge", f"origin/{branch}", 
                        "-m", f"Auto-merge safe changes from {branch}"
                    ])
                else:
                    print(f"⚠️  conflict در برنچ {branch}: {conflicts}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ خطا در merge خودکار: {e}")
            return False
    
    def run_analysis(self) -> None:
        """اجرای تحلیل کامل"""
        print("🔍 شروع تحلیل برنچ‌های Integration...")
        
        # بروزرسانی برنچ‌ها
        print("📡 بروزرسانی اطلاعات git...")
        self.run_git_command(["git", "fetch", "origin"])
        
        # تحلیل برنچ‌ها
        analysis_results = []
        for branch in self.integration_branches:
            result = self.get_branch_diff(self.main_branch, branch)
            analysis_results.append(result)
        
        # ایجاد طرح merge
        merge_plan = self.create_merge_plan(analysis_results)
        
        # تولید گزارش
        report = self.generate_report(analysis_results, merge_plan)
        
        # ذخیره گزارش
        report_file = f"branch_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 گزارش ذخیره شد: {report_file}")
        print("\n" + "="*50)
        print(report)
        
        # پرسش برای merge خودکار
        if merge_plan["critical_files"]:
            answer = input("\n❓ آیا می‌خواهید merge خودکار انجام شود؟ (y/n): ")
            if answer.lower() in ['y', 'yes', 'بله']:
                success = self.auto_merge_safe_files(merge_plan)
                if success:
                    print("✅ merge خودکار با موفقیت انجام شد!")
                else:
                    print("❌ merge خودکار ناموفق - نیاز به دخالت دستی")


def main():
    """تابع اصلی"""
    if not os.path.exists('.git'):
        print("❌ این پوشه یک repository گیت نیست!")
        sys.exit(1)
    
    analyzer = GitBranchAnalyzer()
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
