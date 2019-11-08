from jinja2 import Environment, FileSystemLoader

class Template(object):
    """docstring for Template"""
    def __init__(self, path):
        super(Template, self).__init__()
        self.env = Environment(loader=FileSystemLoader(path))

    def get(self, template_name):
        return self.env.get_template(template_name + '.html')

    def render(self, name, dic):
        template = self.get(name)
        content = template.render(dic)
        return content