import dspy
import requests
import re
import argparse
from typing import Any, Dict
from tqdm import tqdm

lm = dspy.LM("gemini/gemini-2.5-flash", max_tokens=20000)
lm_mini = dspy.LM("gemini/gemini-2.5-pro", max_tokens=10000)
dspy.configure(lm=lm)

class TextbookReadabilityCritique(dspy.Signature):
    """Analyze textbook content for readability, clarity, and pedagogical quality."""
    textbook_analysis: dict[str, Any] = dspy.InputField(desc="Hierarchical textbook content (Chapters, Sections).")
    target_audience: str = dspy.InputField(desc="Intended audience level.")
    readability_analysis: str = dspy.OutputField(desc="Evaluation of sentence structure, cognitive load, jargon.")
    actionable_suggestions: str = dspy.OutputField(desc="Specific suggestions for improvement.")

def download_and_chunk_text(url: str, context_window: int = 8000) -> Dict[str, Any]:
    """Download text and chunk at paragraph boundaries based on context window size."""
    print(f"📥 Downloading: {url}")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    text = ""
    with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading") as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                text += chunk.decode('utf-8', errors='ignore')
                pbar.update(len(chunk))
        
    target_size = (context_window // 10) * 4
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    
    chunks, current, size, idx = {}, [], 0, 1
    for para in tqdm(paragraphs, desc="Chunking", unit="para"):
        if size + len(para) > target_size and current:
            chunks[f"Section_{idx:02d}"] = '\n\n'.join(current)
            current, size, idx = [para], len(para), idx + 1
        else:
            current.append(para)
            size += len(para)
    
    if current:
        chunks[f"Section_{idx:02d}"] = '\n\n'.join(current)
    
    print(f"✅ Created {len(chunks)} sections (~{target_size} chars each)")
    return chunks

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit textbook readability using DSPy RLM")
    parser.add_argument("--url", default="https://www.gutenberg.org/cache/epub/1399/pg1399.txt",
                        help="URL of the textbook to analyze")
    parser.add_argument("--audience", default="High School Student",
                        help="Target audience level (e.g., 'High School Student', 'College Freshman')")
    args = parser.parse_args()
    
    textbook_analysis = download_and_chunk_text(args.url)
    auditor = dspy.RLM(TextbookReadabilityCritique, max_iterations=20, sub_lm=lm_mini, verbose=True)
    print("\n🚀 Starting Recursive Audit...\n")
    result = auditor(textbook_analysis=textbook_analysis, target_audience=args.audience)
    print("\n" + "="*40 + "\nFINAL AUDIT REPORT\n" + "="*40)
    print(result)

    with open("textbook_audit_report.txt", 'w') as f:
        f.write(f"{'='*60}\nTEXTBOOK READABILITY AUDIT REPORT\n{'='*60}\n\n")
        for section, content in [("READABILITY ANALYSIS", result.readability_analysis),
                                  ("ACTIONABLE SUGGESTIONS", result.actionable_suggestions)]:
            f.write(f"{section}\n{'-'*60}\n{content}\n\n")
    print("\n✅ Report saved to: textbook_audit_report.txt")
