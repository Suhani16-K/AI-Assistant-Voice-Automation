"""skills/file_ops.py"""
import os, re

class FileOps:
    def __init__(self):
        self.base = os.path.expanduser("~/Desktop")
        os.makedirs(self.base, exist_ok=True)

    def _fname(self, q):
        m = re.search(r'(?:named?|called?|file)\s+["\']?(\w[\w\s\-\.]*)["\']?', q, re.I)
        return (m.group(1).strip().replace(" ","_")+".txt") if m else "nexus_file.txt"

    def create_file(self, q) -> str:
        fp = os.path.join(self.base, self._fname(q))
        open(fp,"w").write("# Created by NEXUS\n")
        return f"File created on Desktop: {self._fname(q)}"

    def read_file(self, q) -> str:
        fp = os.path.join(self.base, self._fname(q))
        if os.path.exists(fp):
            return open(fp).read()[:500]
        return f"File not found: {self._fname(q)}"

    def list_files(self, q="") -> str:
        files = os.listdir(self.base)
        return f"Desktop files: {', '.join(files[:15])}" if files else "Desktop is empty."

    def delete_file(self, q) -> str:
        fp = os.path.join(self.base, self._fname(q))
        if os.path.exists(fp):
            os.remove(fp)
            return f"Deleted: {self._fname(q)}"
        return f"File not found: {self._fname(q)}"
