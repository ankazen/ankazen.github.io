from jinja2x import Template
from pathlib import Path
import yaml
import markdown
import datetime
import codecs


with open('ankazen.yaml') as f:
    content = f.read()
DIC = yaml.load(content)
print(DIC)

THEME_PATH = '../themes/%s/templates' % DIC['theme']
OUT_PATH = '../'
TMP = Template(THEME_PATH)

def props(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not callable(value) and not name.startswith('_'):
            pr[name] = value
    return pr

def seqsplit(seq, func):
    result = []
    group = []
    for item in seq:
        if func(item):
            if group:
                result.append(group)
            group = []
        group.append(item)
    else:
        if group:
            result.append(group)

    return result

def markdownrender(lines):
    result = []
    for line in lines:
        if line.startswith('#'):
            line = '####' + line
        result.append(line)

    result = markdown.markdown('\n'.join(result))
    return result


def renderpage(dic, name='tmp'):
    result = TMP.render(name, dic)
    with open(dic['outfile'], 'w', encoding='utf8') as out:
        out.write(result)


def renderblock(dic):
    result = TMP.render(dic['name'], dic['content'])
    return result


def content4md(path):
    input_file = codecs.open(path, mode="r", encoding="utf-8")
    lines = input_file.readlines()
    content = markdownrender(lines)
    return content

def content4blocks(dic):
    content = []
    for sub in dic:
        result = renderblock(sub)
        content.append(result)
    return ''.join(content)


renderdic = DIC.copy()
index = None
for item in DIC:
    if item != 'links':
        continue
    for link in DIC[item]:
        name = link['name']
        if not index:
            index = name

        if 'content' in link:
            content = content4blocks(link['content'])
            renderdic['name'] = name
            renderdic['content'] = content
            renderdic['outfile'] = OUT_PATH + name+'.html'
            renderpage(renderdic)
        else:
            path = '../docs/' + link['path']
            p = Path(path)
            content = []
            paths = []
            for i in p.iterdir():
                paths.append(i)

            paths.sort(key=lambda item:item.stat().st_ctime, reverse=True)

            for i in paths:
                stem = i.stem
                path = i.resolve()
                renderdic['title'] = stem
                renderdic['name'] = name
                md = content4md(path)
                with open(path, encoding='utf8') as f:
                    lines = f.readlines()
                    summay = markdownrender(lines[:15])
                    date = datetime.datetime.fromtimestamp(i.stat().st_mtime).strftime('%Y-%m-%d %H:%M')

                renderdic['date'] = date
                renderdic['content'] = md
                renderdic['outfile'] = OUT_PATH + name + '/'+stem+'.html'
                renderpage(renderdic, 'blog')

                newdic = {}
                newdic['name'] = name + '_summay'
                newdic['content'] = {'title': stem, 'date':date, 'content': summay}
                content.append(renderblock(newdic))
            content = ''.join(content)
            # print(content)
            renderdic['name'] = name
            renderdic['content'] = content
            renderdic['outfile'] = OUT_PATH + name+'.html'
            renderpage(renderdic)


dic = {}
dic['outfile'] = OUT_PATH + 'index.html'
dic['url'] = index
renderpage(dic, name='index')
