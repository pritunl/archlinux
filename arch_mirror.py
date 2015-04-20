import datetime
import os
import subprocess

MIRROR_SOURCE_ROOT = 'rsync://mirror.rit.edu/archlinux'
MIRROR_DEST_ROOT = '/mirror/archlinux'
PKG_ROOT = '/mirror/archlinux/all'

cur_date = datetime.date.today()

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

base_args = [
    'rsync',
    '-rtlHh',
    '--progress',
    '--delete-after',
    '--delay-updates',
    '--copy-links',
    '--safe-links',
    '--max-delete=1000',
    '--delete-excluded',
    '--exclude=.*',
    '--hard-links',
]

repo_args = []

print '***************************************************'

for repo in ['core', 'extra', 'community']:
    args = list(base_args)

    source = MIRROR_SOURCE_ROOT + '/%s/os/x86_64/' % repo
    print 'source:', source

    dest = os.path.join(MIRROR_DEST_ROOT, cur_date.strftime('%Y/%m/%d'),
        '%s/os/x86_64/' % repo)
    print 'dest:', dest

    link_dest = get_latest_mirror()
    if link_dest:
        link_dest = os.path.join(link_dest, '%s/os/x86_64/' % repo)

        if link_dest != dest:
            args.append('--link-dest=%s' % link_dest)
            print 'link-dest:', link_dest

    args += [
        source,
        dest,
    ]

    repo_args.append(args)

print '***************************************************'

confirm = raw_input('Continue (y/N): ').lower()
if confirm != 'y':
    exit(1)

for args in repo_args:
    if not os.path.exists(args[-1]):
        os.makedirs(args[-1])

    subprocess.check_call(args)

os.remove(os.path.join(MIRROR_DEST_ROOT, 'latest'))
subprocess.check_call(['ln', '-s',
    os.path.join(MIRROR_DEST_ROOT, cur_date.strftime('%Y/%m/%d')),
    os.path.join(MIRROR_DEST_ROOT, 'latest'),
])

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
