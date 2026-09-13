#!/usr/bin/env python3
"""Compile the editable CV and prepare an Overleaf source archive."""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tex-bin', type=Path, help='Optional directory containing latexmk, xelatex, and biber')
    parser.add_argument('--publish', action='store_true', help='Also replace the website PDF after reviewing the draft; does not commit or deploy')
    args = parser.parse_args()
    environment = os.environ.copy()
    if args.tex_bin:
        environment['PATH'] = str(args.tex_bin.resolve()) + os.pathsep + environment.get('PATH', '')
    for command in ['latexmk', 'xelatex', 'biber']:
        if not shutil.which(command, path=environment.get('PATH')):
            parser.error(f'{command} is missing. Install a TeX distribution or supply --tex-bin; see README.md.')
    subprocess.run(['latexmk', '-xelatex', '-interaction=nonstopmode', '-halt-on-error',
                    '-file-line-error', '-outdir=build', 'main.tex'],
                   cwd=ROOT, env=environment, check=True)
    pdf = ROOT / 'Nikhil_Varma_Keetha_CV.pdf'
    shutil.copy2(ROOT / 'build/main.pdf', pdf)
    sources = [ROOT / name for name in ['main.tex', 'style.tex', 'research.bib', 'README.md', 'latexmkrc']]
    sources += sorted((ROOT / 'sections').glob('*.tex'))
    archive = ROOT / 'build/Nikhil_CV_Overleaf.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
        for source in sources:
            bundle.write(source, source.relative_to(ROOT))
    print(f'\nDraft: {pdf}\nOverleaf source: {archive}')
    if args.publish:
        destination = ROOT.parent / 'assets/pdf/Nikhil_CV.pdf'
        shutil.copy2(pdf, destination)
        print(f'Website PDF updated locally: {destination}')


if __name__ == '__main__':
    main()
