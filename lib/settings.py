import yaml

class YamlSettings:

    def __init__(self, yaml_file_path):
        self._yaml_file_path = yaml_file_path
        self._fields = list(self.__annotations__)
        print('self._fields', self._fields)
        self._save_off = False
        try:
            with open(yaml_file_path, 'r') as file:
                data = yaml.safe_load(file)
                for field in data:
                    super().__setattr__(field, data[field])
                # check file and class fields
                need_save = False
                for field in self._fields:
                    try:
                        _ = data[field]
                    except KeyError:
                        print(f'Field {field} not found in {yaml_file_path}')
                        need_save = True
                if need_save:
                    self.save()
        except FileNotFoundError:
            with open(yaml_file_path, 'w') as file:
                self.save()

    def save(self, val_dict: dict=None):
        self._save_off = True
        if val_dict is not None:
            for name, val in val_dict.items():
                setattr(self, name, val)
        self._save_off = False
        print("save ini to file")
        data = {}
        try:
            with open(self._yaml_file_path, 'w') as file:
                for field in self._fields:
                    data[field] = super().__getattribute__(field)
                yaml.dump(data, file)
        except AttributeError:
            pass

    def __setattr__(self, prop, val):
        super().__setattr__(prop, val)
        try:
            _ = self._fields
            if prop in self._fields:
                print('save', prop, val)
                if not self._save_off:
                    self.save()
        except AttributeError:
            return

class SettingsGui:
    col_start = 5
    s_dict = {}
    def row(self, d, text):
        return (f'<div class="row mb-1"><div class="col-{self.col_start}">{text}</div>'
                f'<div class="col-{12 - self.col_start}">{d}</div></div>')

class SettingsGUISelect(SettingsGui):
    def __init__(self, prop, name, text, val_list: list):
        self.prop = prop
        self.name = name
        self.text = text
        self.type_fn = prop.__class__
        self.val_list = val_list
        SettingsGui.s_dict[name] = self

    def __str__(self):
        ret_val = f'<select data-name="{self.name}" class="form-select form-select-sm">'
        for item in self.val_list:
            if item == self.prop:
                ret_val += f'<option selected value="{item}">{item}</option>'
            else:
                ret_val += f'<option value="{item}">{item}</option>'
        ret_val += '</select>'
        return self.row(ret_val, self.text)

class SettingsGUIInput(SettingsGui):
    def __init__(self, prop, name, text, attr=''):
        self.prop = prop
        self.name = name
        self.text = text
        self.attr = attr
        self.type_fn = prop.__class__
        SettingsGui.s_dict[name] = self

    def __str__(self):
        ret_val = f'<input data-name="{self.name}" class="form-control form-control-sm" value="{self.prop}" {self.attr}/>'
        return self.row(ret_val, self.text)