#!/usr/bin/env python3
"""生成本地可审阅 ZIP，排除工作记录/缓存；不发布。"""
import argparse
from pathlib import Path
import zipfile
from validate_package import ROOT,validate_package

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);a=parser.parse_args()
    errors=validate_package()
    if errors:raise SystemExit('\n'.join(errors))
    dest=a.output.resolve()
    if dest.exists():raise SystemExit('输出已存在，拒绝覆盖。')
    if dest.is_relative_to(ROOT):raise SystemExit('输出应在包目录之外，避免递归包含。')
    dest.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(ROOT.rglob('*')):
            if not file.is_file() or any(x in ('.git','.superpowers','__pycache__','dist') for x in file.relative_to(ROOT).parts) or file.suffix=='.pyc':continue
            if file.is_symlink():raise SystemExit('打包不采用符号链接。')
            archive.write(file,'gitflow/'+str(file.relative_to(ROOT)))
    print(dest)
