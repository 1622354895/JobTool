from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from job_tracker.excel_builder import save_template


if __name__ == "__main__":
    print(save_template(ROOT / "求职投递管理工具.xlsx"))
