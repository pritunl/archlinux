import os
import subprocess

MIRROR_DEST_ROOT = '/mirror/archlinux'
PKG_ROOT = '/mirror/archlinux/all'

def get_latest_mirror():
    path = MIRROR_DEST_ROOT

    for i in xrange(3):
        dirs = os.listdir(path)
        try:
            dirs.remove('latest')
        except ValueError:
            pass
        try:
            dirs.remove('all')
        except ValueError:
            pass
        if len(dirs) == 0:
            return
        latest_dir = sorted(dirs)[-1]
        path = os.path.join(path, latest_dir)

    return path

src_dir = get_latest_mirror()
for repo in ['core', 'extra', 'community']:
    path = os.path.join(src_dir, repo, 'os/x86_64')
    for pkg_name in os.listdir(path):
        if pkg_name.endswith('sig'):
            continue

        pkg_short = pkg_name.replace('-any.pkg.tar.xz', '')
        pkg_short = pkg_short.replace('-x86_64.pkg.tar.xz', '')

        pkg_path = os.path.join(path, pkg_name)
        sig_path = pkg_path + '.sig'

        pkg_out_path = os.path.join(PKG_ROOT, pkg_short)
        sig_out_path = pkg_out_path + '.sig'

        subprocess.check_call(['ln', '-sfn', pkg_path, pkg_out_path])
        subprocess.check_call(['ln', '-sfn', sig_path, sig_out_path])
