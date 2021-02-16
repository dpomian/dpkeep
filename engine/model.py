import re


class Model:
    def add_entry(self, data_dict, **kwargs):
        if 'name' not in kwargs or kwargs['name'] is None or not self._is_name_valid(kwargs['name']):
            raise ValueError("name is invalid")

        name = kwargs['name']
        link = kwargs['link'] if 'link' in kwargs else None
        pwd = kwargs['pwd'] if 'pwd' in kwargs else None
        tags = kwargs['tags'] if 'tags' in kwargs else None

        if link is None or pwd is None or name is None:
            raise ValueError('attributes cannot be empty')
        if not link.startswith('http://') and not link.startswith('https://'):
            link = 'http://{}'.format(link)

        if name in data_dict:
            raise ValueError("name already exists")

        data_dict[name] = {}
        data_dict[name]["link"] = link
        data_dict[name]["pwd"] = pwd
        if tags:
            data_dict[name]["tags"] = tags

        return data_dict

    def remove_entry(self, data_dict, name):
        if name in data_dict:
            data_dict.pop(name)
        return data_dict

    def update_entry(self, data_dict, **kwargs):
        name = None
        if 'name' in kwargs and kwargs['name'] is not None:
            name = kwargs['name']
        if name and name in data_dict:
            if 'link' in kwargs and kwargs['link']:
                data_dict[name]['link'] = kwargs['link']
            if 'pwd' in kwargs and kwargs['pwd']:
                data_dict[name]['pwd'] = kwargs['pwd']
            if 'tags' in kwargs and kwargs['tags']:
                data_dict[name]['tags'] = kwargs['tags']
        return data_dict

    def _is_name_valid(self, name):
        return re.match(r'^\w+$', name)
