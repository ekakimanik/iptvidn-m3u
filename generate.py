import re, time, urllib.request

UA = "Mozilla/5.0 (Linux; Android 16; RMX3853) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.137 Mobile Safari/537.36"
SITE = "http://iptvidn.com"

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": SITE + "/"})
    return urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")

home = get(SITE + "/")

ids = []
for sid in re.findall(r"play\.php\?stream=([^'\"&<> ]+)", home):
    if sid not in ids:
        ids.append(sid)

logos = {}
for sid, logo in re.findall(r"play\.php\?stream=([^'\"&<> ]+)'\"[^>]*>\s*<img src=\"([^\"]+)\"", home):
    logos[sid] = logo.replace(" ", "%20")

lines = ["#EXTM3U"]
ok = 0
for sid in ids:
    try:
        page = get(SITE + "/play.php?stream=" + sid)
    except Exception:
        print("SKIP:", sid)
        continue
    m = re.search(r"(\d+\.\d+\.\d+\.\d+:\d+)/([^/\"' <>]+)/embed\.html\?token=([0-9a-f-]+)", page)
    if not m:
        print("SKIP:", sid)
        continue
    host, name, token = m.groups()
    logo = ' tvg-logo="%s/%s"' % (SITE, logos[sid]) if sid in logos else ""
    lines.append('#EXTINF:-1 tvg-id="%s"%s,%s' % (sid, logo, sid.replace("-", " ")))
    lines.append("http://%s/%s/index.m3u8?token=%s" % (host, name, token))
    ok += 1
    time.sleep(0.1)

if ok == 0:
    print("কোনো চ্যানেল পাওয়া যায়নি")
    raise SystemExit(1)

open("playlist.m3u", "w").write("\n".join(lines) + "\n")
print(ok, "channels")
